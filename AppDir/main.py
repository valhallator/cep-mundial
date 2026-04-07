#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CULTURA EM PESO BATTLE
Tournament Bracket System - Single Elimination
Side-by-side tournament for up to 44 participants (22 per side)
Author: Copilot
Date: 2026
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import os
import sys
import math
from dataclasses import dataclass, asdict, field
from typing import List, Optional, Dict, Any
from enum import Enum
import threading
from pathlib import Path

# Try to import PIL for watermark
try:
    from PIL import Image, ImageTk
    HAVE_PIL = True
except ImportError:
    HAVE_PIL = False
    print("⚠️  PIL não instalada - watermark desativada")


# ============================================================================
# ASSET PATH HELPER (for PyInstaller --onefile compatibility)
# ============================================================================

def get_asset_path(filename: str) -> str:
    """
    Encontra o caminho correto para um arquivo de asset.
    Funciona tanto para execução direta quanto para PyInstaller --onefile.
    """
    # Se estamos em um pacote PyInstaller --onefile
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        # Execução direta (python main.py)
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    asset_path = os.path.join(base_path, filename)
    return asset_path


def get_data_path(filename: str) -> str:
    """
    Encontra o caminho para dados persistentes (JSON).
    Salva no diretório home do usuário para funcionar com NTFS/permissões diferentes.
    """
    app_data_dir = os.path.expanduser("~/.cultura_em_peso")
    os.makedirs(app_data_dir, exist_ok=True)
    return os.path.join(app_data_dir, filename)


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class Match:
    """Representa um match"""
    match_id: str
    round_name: str
    team1: Optional[str] = None
    team2: Optional[str] = None
    winner: Optional[str] = None
    
    def is_complete(self) -> bool:
        return self.winner is not None
    
    def has_bye(self) -> bool:
        return (self.team1 is None) or (self.team2 is None)


@dataclass
class Tournament:
    """Dados do torneio"""
    left_participants: List[str] = field(default_factory=list)
    right_participants: List[str] = field(default_factory=list)
    left_bracket: Dict[str, List[Match]] = field(default_factory=dict)
    right_bracket: Dict[str, List[Match]] = field(default_factory=dict)
    champion_left: Optional[str] = None
    champion_right: Optional[str] = None
    final_winner: Optional[str] = None


# ============================================================================
# TOURNAMENT LOGIC
# ============================================================================

class BracketManager:
    """Gerencia criação e manipulação de brackets"""
    
    @staticmethod
    def create_bracket(participants: List[str]) -> Dict[str, List[Match]]:
        """
        Cria bracket a partir de lista de participantes.
        Se ímpar, cria repescagem automática.
        """
        
        # Handling odd numbers with playoff
        original_count = len(participants)
        
        if original_count % 2 != 0:
            # Odd number - create playoff for last 3
            playoff_participants = participants[-3:]
            participants = participants[:-3]
            
            # Create playoff round (3 participants, 1 gets bye)
            playoff_round = []
            playoff_round.append(Match(
                match_id=f"playoff_1",
                round_name="REPESCAGEM",
                team1=playoff_participants[0],
                team2=playoff_participants[1],
                winner=None
            ))
            playoff_round.append(Match(
                match_id=f"playoff_2",
                round_name="REPESCAGEM",
                team1=playoff_participants[2],
                team2=None,  # Bye
                winner=None
            ))
            
            bracket = {"REPESCAGEM": playoff_round}
        else:
            bracket = {}
        
        # Standard bracket creation for even number
        num_participants = len(participants)
        
        if num_participants == 0:
            return bracket
        
        # Calculate rounds needed
        num_rounds = math.ceil(math.log2(num_participants))
        
        # Create rounds
        current_participants = participants
        current_round_num = 1
        
        for round_idx in range(num_rounds):
            round_name = BracketManager._get_round_name(num_participants, round_idx)
            round_matches = []
            
            # Create matches
            for i in range(0, len(current_participants), 2):
                team1 = current_participants[i] if i < len(current_participants) else None
                team2 = current_participants[i + 1] if i + 1 < len(current_participants) else None
                
                match = Match(
                    match_id=f"{round_name}_{i//2}",
                    round_name=round_name,
                    team1=team1,
                    team2=team2,
                    winner=None
                )
                round_matches.append(match)
            
            bracket[round_name] = round_matches
            
            # Prepare next round (all teams stay as None placeholders)
            current_participants = [None] * len(round_matches)
            current_round_num += 1
        
        return bracket
    
    @staticmethod
    def _get_round_name(total: int, round_idx: int) -> str:
        """Retorna nome da rodada"""
        # Calculate which round this is based on participants
        rounds_map = {
            2: ["FINAL"],
            4: ["SEMIFINAL", "FINAL"],
            8: ["QUARTAS", "SEMIFINAL", "FINAL"],
            16: ["OITAVAS", "QUARTAS", "SEMIFINAL", "FINAL"],
            32: ["1ª FASE", "OITAVAS", "QUARTAS", "SEMIFINAL", "FINAL"],
        }
        
        # Find closest match
        closest = min(rounds_map.keys(), key=lambda x: abs(x - total))
        names = rounds_map.get(closest, [f"RODADA {round_idx + 1}"])
        
        if round_idx < len(names):
            return names[round_idx]
        return f"RODADA {round_idx + 1}"
    
    @staticmethod
    def advance_winner(bracket: Dict, round_name: str, match_idx: int, winner: str):
        """Avança vencedor para próxima rodada"""
        if round_name not in bracket:
            return
        
        matches = bracket[round_name]
        if match_idx >= len(matches):
            return
        
        matches[match_idx].winner = winner
        
        # Find next round
        round_list = list(bracket.keys())
        try:
            current_idx = round_list.index(round_name)
            if current_idx + 1 < len(round_list):
                next_round_name = round_list[current_idx + 1]
                next_matches = bracket[next_round_name]
                
                # Calculate position in next round
                next_pos = match_idx // 2
                if next_pos < len(next_matches):
                    if match_idx % 2 == 0:
                        next_matches[next_pos].team1 = winner
                    else:
                        next_matches[next_pos].team2 = winner
        except (ValueError, IndexError):
            pass


# ============================================================================
# MAIN GUI
# ============================================================================

class CulturaEmPesoBattle:
    def __init__(self, root):
        self.root = root
        self.root.title("CULTURA EM PESO BATTLE")
        self.root.geometry("1600x900")
        
        self.tournament = Tournament()
        self.bg_image_tk = None
        self.watermark_photo = None
        
        self.setup_ui()
        self.load_tournament()
    
    def setup_ui(self):
        """Setup da interface"""
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas com watermark
        self.canvas = tk.Canvas(main_frame, bg="#1a1a2e", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Frame dentro do canvas
        self.canvas_frame = tk.Frame(self.canvas, bg="#1a1a2e")
        self.canvas_window = self.canvas.create_window(0, 0, window=self.canvas_frame, anchor="nw")
        
        # Bind resize
        self.root.bind("<Configure>", self._on_window_resize)
        
        # ===== HEADER =====
        header = tk.Frame(self.canvas_frame, bg="#16213e", height=150)
        header.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        # Logo attempt
        self._setup_logo(header)
        
        # Title
        title_frame = tk.Frame(header, bg="#16213e")
        title_frame.pack(fill=tk.X, expand=True)
        
        tk.Label(title_frame, text="www.culturaempeso.com | @culturaempeso",
                font=("Arial", 10), bg="#16213e", fg="#1db80e").pack()
        
        self.title_label = tk.Label(title_frame, text="CULTURA EM PESO BATTLE",
                                   font=("Arial", 20, "bold"), bg="#16213e", fg="white")
        self.title_label.pack(pady=10)
        
        # ===== INPUT SECTION =====
        input_frame = tk.LabelFrame(self.canvas_frame, text="ADICIONAR PARTICIPANTES",
                                   font=("Arial", 12, "bold"), bg="#1a1a2e", fg="white",
                                   padx=10, pady=10)
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(input_frame, text="Cole nomes aqui (um por linha ou separados por quebra):",
                bg="#1a1a2e", fg="white", font=("Arial", 10)).pack(anchor="w")
        
        self.input_text = tk.Text(input_frame, height=6, width=80, bg="#0f3460", fg="white",
                                 font=("Courier", 10), insertbackground="white")
        self.input_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Buttons
        btn_frame = tk.Frame(input_frame, bg="#1a1a2e")
        btn_frame.pack(fill=tk.X, pady=5)
        
        tk.Button(btn_frame, text="ADICIONAR À ESQUERDA", command=self._add_left,
                 bg="#1f5f8f", fg="white", font=("Arial", 10, "bold"), padx=10, pady=5).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="ADICIONAR À DIREITA", command=self._add_right,
                 bg="#1f5f8f", fg="white", font=("Arial", 10, "bold"), padx=10, pady=5).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="GERAR CHAVEAMENTO", command=self._generate_bracket,
                 bg="#1db80e", fg="black", font=("Arial", 10, "bold"), padx=10, pady=5).pack(side=tk.LEFT, padx=5)
        
        # Lists
        lists_frame = tk.Frame(self.canvas_frame, bg="#1a1a2e")
        lists_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Left list
        left_frame = tk.LabelFrame(lists_frame, text="ESQUERDA (0/22)",
                                  font=("Arial", 10, "bold"), bg="#1a1a2e", fg="white",
                                  padx=5, pady=5)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.left_listbox = tk.Listbox(left_frame, bg="#0f3460", fg="white",
                                      font=("Courier", 9), height=10)
        self.left_listbox.pack(fill=tk.BOTH, expand=True)
        
        # Right list
        right_frame = tk.LabelFrame(lists_frame, text="DIREITA (0/22)",
                                   font=("Arial", 10, "bold"), bg="#1a1a2e", fg="white",
                                   padx=5, pady=5)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.right_listbox = tk.Listbox(right_frame, bg="#0f3460", fg="white",
                                       font=("Courier", 9), height=10)
        self.right_listbox.pack(fill=tk.BOTH, expand=True)
        
        # ===== BRACKET SECTION =====
        self.bracket_frame = tk.Frame(self.canvas_frame, bg="#1a1a2e")
        self.bracket_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Bind scroll
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)
    
    def _setup_logo(self, parent):
        """Setup logo como watermark"""
        logo_path = get_asset_path("logo.png")
        if not HAVE_PIL or not os.path.exists(logo_path):
            return
        
        try:
            img = Image.open(logo_path)
            # Resize
            img.thumbnail((200, 200), Image.Resampling.LANCZOS)
            # Add alpha
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            # Make semi-transparent
            alpha = img.split()[3]
            alpha = alpha.point(lambda p: int(p * 0.3))
            img.putalpha(alpha)
            
            self.watermark_photo = ImageTk.PhotoImage(img)
            tk.Label(parent, image=self.watermark_photo, bg="#16213e").pack()
        except Exception as e:
            print(f"Logo error: {e}")
    
    def _add_left(self):
        """Adiciona à esquerda"""
        text = self.input_text.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Aviso", "Cole nomes primeiro!")
            return
        
        # Parse names
        names = [n.strip() for n in text.replace(",", "\n").split("\n") if n.strip()]
        
        self.tournament.left_participants.extend(names)
        self.input_text.delete("1.0", tk.END)
        self._update_lists()
    
    def _add_right(self):
        """Adiciona à direita"""
        text = self.input_text.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Aviso", "Cole nomes primeiro!")
            return
        
        # Parse names
        names = [n.strip() for n in text.replace(",", "\n").split("\n") if n.strip()]
        
        self.tournament.right_participants.extend(names)
        self.input_text.delete("1.0", tk.END)
        self._update_lists()
    
    def _update_lists(self):
        """Atualiza exibição das listas"""
        self.left_listbox.delete(0, tk.END)
        for i, name in enumerate(self.tournament.left_participants, 1):
            self.left_listbox.insert(tk.END, f"{i}. {name}")
        
        self.right_listbox.delete(0, tk.END)
        for i, name in enumerate(self.tournament.right_participants, 1):
            self.right_listbox.insert(tk.END, f"{i}. {name}")
        
        # Update labels
        left_count = len(self.tournament.left_participants)
        right_count = len(self.tournament.right_participants)
    
    def _generate_bracket(self):
        """Gera chaveamento"""
        left_count = len(self.tournament.left_participants)
        right_count = len(self.tournament.right_participants)
        
        if left_count < 2 or right_count < 2:
            messagebox.showwarning("Aviso", "Mínimo 2 participantes por lado!")
            return
        
        # Create brackets
        self.tournament.left_bracket = BracketManager.create_bracket(self.tournament.left_participants)
        self.tournament.right_bracket = BracketManager.create_bracket(self.tournament.right_participants)
        
        self._display_bracket()
        self.save_tournament()
    
    def _display_bracket(self):
        """Exibe o bracket"""
        # Clear
        for widget in self.bracket_frame.winfo_children():
            widget.destroy()
        
        if not self.tournament.left_bracket and not self.tournament.right_bracket:
            empty_label = tk.Label(self.bracket_frame, text="Gere um chaveamento para começar!",
                                  bg="#1a1a2e", fg="#666", font=("Arial", 14))
            empty_label.pack(expand=True)
            return
        
        # Main container
        container = tk.Frame(self.bracket_frame, bg="#1a1a2e")
        container.pack(fill=tk.BOTH, expand=True)
        
        # Left side
        left_side = tk.LabelFrame(container, text="LADO ESQUERDA",
                                 font=("Arial", 12, "bold"), bg="#1a1a2e", fg="white",
                                 padx=10, pady=10)
        left_side.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self._draw_side(left_side, self.tournament.left_bracket, "left")
        
        # Center - Final
        final_frame = tk.Frame(container, bg="#1a1a2e", width=200)
        final_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=5)
        self._draw_final(final_frame)
        
        # Right side
        right_side = tk.LabelFrame(container, text="LADO DIREITA",
                                  font=("Arial", 12, "bold"), bg="#1a1a2e", fg="white",
                                  padx=10, pady=10)
        right_side.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self._draw_side(right_side, self.tournament.right_bracket, "right")
    
    def _draw_side(self, parent, bracket: Dict, side: str):
        """Desenha um lado do bracket"""
        if not bracket:
            return
        
        for round_name, matches in bracket.items():
            round_frame = tk.LabelFrame(parent, text=round_name,
                                       font=("Arial", 10, "bold"), bg="#1a1a2e", fg="white",
                                       padx=5, pady=5)
            round_frame.pack(fill=tk.BOTH, expand=True, pady=5)
            
            for match_idx, match in enumerate(matches):
                self._draw_match(round_frame, match, round_name, match_idx, side)
    
    def _draw_match(self, parent, match: Match, round_name: str, match_idx: int, side: str):
        """Desenha um match"""
        match_frame = tk.Frame(parent, bg="#1f5f8f", relief=tk.RAISED, bd=2)
        match_frame.pack(fill=tk.X, padx=5, pady=3)
        
        # Team 1
        team1_text = match.team1 if match.team1 else "---"
        team1_btn = tk.Label(match_frame, text=team1_text,
                            bg="#1f5f8f" if match.winner != match.team1 else "#1db80e",
                            fg="white", font=("Arial", 9, "bold"),
                            padx=10, pady=5, cursor="hand2" if match.team1 else "")
        team1_btn.pack(fill=tk.X)
        
        if match.team1 and not match.has_bye():
            def mark_winner_1(evt, t=match.team1, r=round_name, m=match_idx, s=side):
                self._mark_winner(t, r, m, s)
            team1_btn.bind("<Button-1>", mark_winner_1)
        
        # VS
        vs_label = tk.Label(match_frame, text="VS",
                           bg="#1f5f8f", fg="#aaa", font=("Arial", 8))
        vs_label.pack()
        
        # Team 2
        team2_text = match.team2 if match.team2 else "---"
        team2_btn = tk.Label(match_frame, text=team2_text,
                            bg="#1f5f8f" if match.winner != match.team2 else "#1db80e",
                            fg="white", font=("Arial", 9, "bold"),
                            padx=10, pady=5, cursor="hand2" if match.team2 else "")
        team2_btn.pack(fill=tk.X)
        
        if match.team2 and not match.has_bye():
            def mark_winner_2(evt, t=match.team2, r=round_name, m=match_idx, s=side):
                self._mark_winner(t, r, m, s)
            team2_btn.bind("<Button-1>", mark_winner_2)
    
    def _mark_winner(self, team: str, round_name: str, match_idx: int, side: str):
        """Marca vencedor"""
        bracket = self.tournament.left_bracket if side == "left" else self.tournament.right_bracket
        BracketManager.advance_winner(bracket, round_name, match_idx, team)
        
        # Check if someone won
        last_round = list(bracket.keys())[-1]
        if match_idx < len(bracket[last_round]):
            match = bracket[last_round][0]  # Final match
            if match.winner:
                if side == "left":
                    self.tournament.champion_left = match.winner
                else:
                    self.tournament.champion_right = match.winner
        
        self._display_bracket()
        self.save_tournament()
        self._check_final()
    
    def _draw_final(self, parent):
        """Desenha final"""
        if not self.tournament.champion_left or not self.tournament.champion_right:
            empty = tk.Label(parent, text="AGUARDANDO\nCAMPEÕES", bg="#1a1a2e", fg="#666",
                           font=("Arial", 10))
            empty.pack(expand=True)
            return
        
        final_box = tk.LabelFrame(parent, text="🏆 FINAL",
                                 font=("Arial", 12, "bold"), bg="#1a1a2e", fg="#1db80e",
                                 padx=5, pady=10)
        final_box.pack(fill=tk.BOTH, expand=True)
        
        # Left champion
        left_btn = tk.Label(final_box, text=self.tournament.champion_left,
                           bg="#1f5f8f" if self.tournament.final_winner != self.tournament.champion_left else "#1db80e",
                           fg="white", font=("Arial", 10, "bold"), padx=5, pady=10, cursor="hand2")
        left_btn.pack(fill=tk.X, pady=3)
        
        def select_left(evt):
            self.tournament.final_winner = self.tournament.champion_left
            self._show_winner()
        left_btn.bind("<Button-1>", select_left)
        
        tk.Label(final_box, text="VS", bg="#1a1a2e", fg="white", font=("Arial", 8)).pack()
        
        # Right champion
        right_btn = tk.Label(final_box, text=self.tournament.champion_right,
                            bg="#1f5f8f" if self.tournament.final_winner != self.tournament.champion_right else "#1db80e",
                            fg="white", font=("Arial", 10, "bold"), padx=5, pady=10, cursor="hand2")
        right_btn.pack(fill=tk.X, pady=3)
        
        def select_right(evt):
            self.tournament.final_winner = self.tournament.champion_right
            self._show_winner()
        right_btn.bind("<Button-1>", select_right)
    
    def _check_final(self):
        """Verifica se tem final"""
        pass
    
    def _show_winner(self):
        """Mostra vencedor"""
        if self.tournament.final_winner:
            self.title_label.config(text=f"🏆 VENCEDOR: {self.tournament.final_winner}")
            messagebox.showinfo("CAMPEÃO!", f"🏆 {self.tournament.final_winner} É O CAMPEÃO!")
            self.save_tournament()
    
    def _on_mousewheel(self, event):
        """Mousewheel scroll"""
        if event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
    
    def _on_window_resize(self, event):
        """Resiza canvas"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def save_tournament(self):
        """Salva torneio em JSON"""
        try:
            data = {
                "left_participants": self.tournament.left_participants,
                "right_participants": self.tournament.right_participants,
                "champion_left": self.tournament.champion_left,
                "champion_right": self.tournament.champion_right,
                "final_winner": self.tournament.final_winner,
                "left_bracket": self._bracket_to_dict(self.tournament.left_bracket),
                "right_bracket": self._bracket_to_dict(self.tournament.right_bracket),
            }
            
            data_path = get_data_path("tournament_data.json")
            with open(data_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"✅ Torneio salvo em: {data_path}")
        except (IOError, OSError) as e:
            print(f"❌ Erro ao salvar: {e}")
            messagebox.showerror("Erro ao Salvar", f"Não consegui salvar o torneio. Verifique permissões:\n{e}")
        except Exception as e:
            print(f"❌ Erro inesperado ao salvar: {e}")
            messagebox.showerror("Erro", f"Erro ao salvar torneio: {e}")
    
    def load_tournament(self):
        """Carrega torneio do JSON"""
        data_path = get_data_path("tournament_data.json")
        if not os.path.exists(data_path):
            return
        
        try:
            with open(data_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            self.tournament.left_participants = data.get("left_participants", [])
            self.tournament.right_participants = data.get("right_participants", [])
            self.tournament.champion_left = data.get("champion_left")
            self.tournament.champion_right = data.get("champion_right")
            self.tournament.final_winner = data.get("final_winner")
            
            self._update_lists()
            
            if data.get("left_bracket"):
                self._display_bracket()
        except json.JSONDecodeError as e:
            print(f"❌ Erro ao parsear JSON: {e}")
            messagebox.showerror("Erro", f"Arquivo de torneio corrompido: {e}")
        except (IOError, OSError) as e:
            print(f"❌ Erro ao ler arquivo: {e}")
            messagebox.showerror("Erro", f"Não consegui ler arquivo de torneio. Verifique permissões: {e}")
        except Exception as e:
            print(f"❌ Erro ao carregar: {e}")
            messagebox.showerror("Erro", f"Erro inesperado ao carregar torneio: {e}")
    
    def _bracket_to_dict(self, bracket: Dict) -> Dict:
        """Converte bracket para dict"""
        result = {}
        for round_name, matches in bracket.items():
            result[round_name] = [asdict(m) for m in matches]
        return result


# ============================================================================
# MAIN
# ============================================================================

def main():
    root = tk.Tk()
    app = CulturaEmPesoBattle(root)
    root.mainloop()


if __name__ == "__main__":
    main()
