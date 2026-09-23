import math
import random
import tkinter as tk
from random import choice
from tkinter import messagebox
import copy



class Agent:
    def __init__(self, name, preferences, personality="Regular"):
        self.name = name
        self.preferences = preferences
        self.personality = personality

    def Get_personality_multiplier(self):
        if self.personality == "Greedy":
            return 1.3
        elif self.personality == "Selfless":
            return 0.7
        else:
            return 1.0


    def get_value_of_interval(self, start, end, total_slices):
        if start >= end:
            return 0.0

        start = max(0.0, min(1.0, start))
        end = max(0.0, min(1.0, end))

        if start >= end:
            return 0.0

        value = 0.0
        for i in range(total_slices):
            slice_start = float(i) / total_slices
            slice_end = float(i + 1) / total_slices

            overlap_start = max(start, slice_start)
            overlap_end = min(end, slice_end)

            if overlap_start < overlap_end:
                fraction = (overlap_end - overlap_start) / (slice_end - slice_start)
                value += fraction * self.preferences[i]

        return value

    def get_value_of_bundle(self, intervals, total_slices):
        return sum(self.get_value_of_interval(s, e, total_slices) for s, e in intervals)


def find_simple_cut(agent, start, end, target_value, total_slices):
    low, high = start, end

    if target_value <= 0:
        return start



    for i in range(50):
        mid = (low + high) / 2.0
        value = agent.get_value_of_interval(start, mid, total_slices)
        if value <= target_value:
            low = mid
        else:
            high = mid
    return high


def merge_intervals(intervals):
    if not intervals:
        return []
    intervals.sort(key=lambda x: x[0])
    merged = []
    for start, end in intervals:
        if not merged or abs(merged[-1][1] - start) > 1e-6:
            merged.append([start, end])
        else:
            merged[-1][1] = max(merged[-1][1], end)
    return [(start, end) for start, end in merged if end - start > 1e-6]

# I Cut, You Choose (two player game)
def ICutUChoose(agent, total_slices):
    a, b = agent[0], agent[1]
    allocation = {a.name: [], b.name: []}

    yield ("log", "I Cut You Choose - For Two Players")
    yield ("log", f"Cutter: {a.name} | Chooser: {b.name}")
    yield ("log", "")

    a_total = sum(a.preferences) / 2.0

    if a.personality == "Greedy":
        target = a_total * 0.8
    elif a.personality == "Selfless":
        target = a_total * 1.2
    else:
        target = a_total

    yield ("log", f"{a.name}'s Target: {target}")

    cutting_point = find_simple_cut(a, 0.0, 1.0, target, total_slices)
    piece1 = (0.0, cutting_point)
    piece2 = (cutting_point, 1.0)

    yield ("log", "")
    yield ("log", f"Cut Point: {cutting_point}")
    yield ("log", f"Piece 1: [0.000 - {piece1[1]:.3f}] (Value to {a.name}: {a.get_value_of_interval(0.0, cutting_point, total_slices):.2f})")
    yield ("log", f"Piece 2: [{piece2[0]:.3f} - 1.000] (Value to {a.name}: {a.get_value_of_interval(cutting_point, 1.0, total_slices):.2f})")

    b_value1 = b.get_value_of_interval(piece1[0], piece1[1], total_slices)
    b_value2 = b.get_value_of_interval(piece2[0], piece2[1], total_slices)

    yield ("log", "")
    yield ("log", f"{b.name}'s Values")
    yield ("log", f"Piece 1: {b_value1:.2f}")
    yield ("log", f"Piece 2: {b_value2:.2f}")

    if b.personality == "Selfless":
        if b_value1 >= b_value2 * 0.8:
            yield ("log", f"\n{b.name}(Selfless) chooses Piece 1 (even through slice might be less valuable)")
            allocation[b.name] = [piece1]
            allocation[a.name] = [piece2]
        else:
            yield ("log", f"\n{b.name}(Selfless) chooses Piece 2")
            allocation[b.name] = [piece2]
            allocation[a.name] = [piece1]

    elif b.personality == "Greedy":
        if b_value1 >= b_value2:
            yield ("log", f"\n{b.name}(Greedy) chooses Piece 1 (Takes bigger Piece")
            allocation[b.name] = [piece1]
            allocation[a.name] = [piece2]
        else:
            yield ("log", f"\n{b.name}(Greedy) chooses Piece 2")
            allocation[b.name] = [piece2]
            allocation[a.name] = [piece1]
    else:
        if b_value1 >= b_value2:
            yield ("log", f"\n{b.name}(Regular) chooses Piece 1 (Takes bigger Piece")
            allocation[b.name] = [piece1]
            allocation[a.name] = [piece2]
        else:
            yield ("log", f"\n{b.name}(Regular) chooses Piece 2")
            allocation[b.name] = [piece2]
            allocation[a.name] = [piece1]

    yield ("state", allocation, "Allocation Finalised")
    yield from Verify_Results(agent, allocation, total_slices)


# Selfridge-Conway (Three Player Game)
def Selfridge_Conway(agent, total_slices):
    A, B, C = agent[0], agent[1], agent[2]
    allocation = {A.name: [] for a in agent}

    yield ("log", "Selfridge-Conway - For Three Players")
    yield ("log", f"Players: {A.name}, {B.name} , {C.name}")
    yield ("log", "")

    yield ("log", f"Stage 1: Player {A.name} divides the cake into what they think is 3 equal pieces")
    yield ("log", "")

    a_total = sum(A.preferences)

    if A.personality == "Greedy":
        target = a_total/3.0 * 0.8
        yield ("log", f"{A.name}(Greedy) cuts piece slightly uneven, Target: {target:.2f} per piece")
    elif A.personality == "Selfless":
        target = a_total/3.0 * 1.2
        yield ("log", f"{A.name}(Selfless) cuts piece Generously, Target: {target:.2f} per piece")
    else:
        target = a_total/3.0
        yield ("log", f"{A.name}(Regular) cuts piece evenly, Target: {target:.2f} per piece")

    cut1 = find_simple_cut(A, 0.0, 1.0, target, total_slices)
    cut2 = find_simple_cut(A, cut1, 1.0, target, total_slices)

    p1 = (0.0, cut1)
    p2 = (cut1, cut2)
    p3 = (cut2, 1.0)
    pieces = [p1, p2, p3]

    yield ("log", "")

    yield ("log", f"Piece 1: [{p1[0]:.3f} - {p1[1]:.3f}] (Value to {A.name}: {A.get_value_of_interval(p1[0], p1[1], total_slices):.2f})")
    yield ("log", f"Piece 2: [{p2[0]:.3f} - {p2[1]:.3f}] (Value to {A.name}: {A.get_value_of_interval(p2[0], p2[1], total_slices):.2f})")
    yield ("log", f"Piece 3: [{p3[0]:.3f} - {p3[1]:.3f}] (Value to {A.name}: {A.get_value_of_interval(p3[0], p3[1], total_slices):.2f})")

    yield ("state", {A.name: pieces.copy(), B.name: [], C.name: []}, "Stage 1: Cake Cut")

    yield ("log", "")
    yield ("log", f"Stage 2: Player B({B.name}) Evaluaters the piece and trims if one is higher then what they thing is 1/3")

    b_values = [B.get_value_of_interval(p[0], p[1], total_slices) for p in pieces]

    if B.personality == "Greedy":
        trim_threshold = 0.05
    elif B.personality == "Selfless":
        trim_threshold = 0.2
    else:
        trim_threshold = 0.1
    ("log", f"{B.name}({A.personality}) will trim if any piece is more then {trim_threshold:.2f} above other")

    yield ("log", f"{B.name} values pieces at -")
    yield ("log", f"Piece 1: {b_values[0]:.2f}")
    yield ("log", f"Piece 2: {b_values[1]:.2f}")
    yield ("log", f"Piece 3: {b_values[2]:.2f}")
    sorted_idx = sorted(range(len(b_values)), key=lambda i: b_values[i], reverse=True)
    Max_idx, sec_idx = sorted_idx[0], sorted_idx[1]
    trim_amount = b_values[Max_idx] - b_values[sec_idx]

    remnant = None
    trimmed_piece = None

    if trim_amount > trim_threshold:
        yield ("log", f"Piece {Max_idx+1} is the largest by {trim_amount:.2f}, trimming it")
        target_trim_value = b_values[sec_idx]
        original = pieces[Max_idx]
        trim_point = find_simple_cut(B, original[0], original[1], target_trim_value, total_slices)

        trimmed_piece = (original[0], trim_point)
        remnant = (trim_point, original[1])
        pieces[Max_idx] = trimmed_piece

        yield ("log", "")
        yield ("log", f"Trimmed piece: [{trimmed_piece[0]:.2f} - {trimmed_piece[1]:.2f}]")
        yield ("log", f"Remnant: [{remnant[0]:.2f} - {remnant[1]:.2f}]")
    else:
        yield ("log", f"No Trimming Needed - the pieces are basically the same")

    yield ("log", "\nStage 3: Selecting the Pieces")
    yield ("log", "")

    c_vals = [C.get_value_of_interval(p[0], p[1], total_slices) for p in pieces]
    if C.personality == "Selfless":
        c_choice = sorted(range(len(c_vals)), key=lambda i: c_vals[i])[1]
        yield ("log", f"{C.name} (Selfless) choose moderately: Piece {c_choice+1}")
    else:
        c_choice = c_vals.index(max(c_vals))
    c_piece = pieces.pop(c_choice)
    allocation[C.name] = [c_piece]
    yield ("log", f"{C.name} chooses Piece {c_choice+1}: [{c_piece[0]:.2f} - {c_piece[1]:.2f}] (value: {max(c_vals):.2f})")

    if trimmed_piece and trimmed_piece in pieces:
        b_choice_idx = pieces.index(trimmed_piece)
        b_piece = pieces.pop(b_choice_idx)
        allocation[B.name] = [b_piece]
        yield ("log", f"{B.name} (Trimmer) has to take trimmed piece: [{b_piece[0]:.2f} - {b_piece[1]:.2f}]")
    else:
        b_vals_remain = [B.get_value_of_interval(p[0], p[1], total_slices) for p in pieces]
        if B.personality == "Selfless":
            b_choice = sorted(range(len(b_vals_remain)), key=lambda i: b_vals_remain[i])[1]
        else:
            b_choice = b_vals_remain.index(max(b_vals_remain))
        b_piece = pieces.pop(b_choice)
        allocation[B.name] = [b_piece]
        yield ("log", f"{B.name} chooses Piece {b_choice+1}: [{b_piece[0]:.2f} - {b_piece[1]:.2f}] (value: {max(b_vals_remain):.2f})")

    a_piece = pieces[0]
    allocation[A.name] = [a_piece]
    yield ("log", f"{A.name} gets remaining piece: [{a_piece[0]:.2f} - {a_piece[1]:.2f}]")

    yield ("state", allocation, "Main Cake Give Out")

    if remnant:
        yield ("log", "\nStage 4: Remnent division")
        yield ("log", "")

        if c_piece == trimmed_piece:
            t_agent, nont_agent = C, B
        else :
            t_agent, nont_agent = B, C

        yield ("log", f"Remnant divided by {nont_agent.name}, chosen by {t_agent.name}")

        r_start, r_end = remnant
        r_step = (r_end - r_start) / 3.0
        rem_piece = [
            (r_start, r_start + r_step),
            (r_start + r_step, r_start + (2 * r_step)),
            (r_start + (2 * r_step), r_end),
        ]

        yield ("log", f"Remnant split into: {[f'[{p[0]:.3f}-{p[1]:.3f}]' for p in rem_piece]}")

        t_vals = [t_agent.get_value_of_interval(p[0], p[1], total_slices) for p in rem_piece]
        if t_agent.personality == "Selfless":
            t_idx = t_vals.index(min(t_vals))
            yield("log", f"{t_agent.name} (Selfless) takes smallest piece")
        else:
            t_idx = t_vals.index(max(t_vals))
        t_piece = rem_piece.pop(t_idx)
        allocation[t_agent.name].append(t_piece)
        yield("log", f"{t_agent.name} takes remnant piece {t_idx+1}: [{t_piece[0]:.2f} - {t_piece[1]:.2f}]")

        a_vals = [A.get_value_of_interval(p[0], p[1], total_slices) for p in rem_piece]
        a_idx = a_vals.index(max(a_vals))
        a_piece_rem = rem_piece.pop(a_idx)
        allocation[A.name].append(a_piece_rem)
        yield("log", f"{A.name} takes remnant: [{a_piece_rem[0]:.2f} - {a_piece_rem[1]:.2f}]")

        nont_piece = rem_piece[0]
        allocation[nont_agent.name].append(nont_piece)
        yield("log", f"{nont_agent.name} takes remnant: [{nont_piece[0]:.2f} - {nont_piece[1]:.2f}]")

        yield("state", allocation, "Remnant Divided")
    yield from Verify_Results(agent, allocation, total_slices)


#Even-Paz
def Even_Paz(agent, total_slices):
    n = len(agent)

    yield ("log", f"Even-Paz - {n} Players")
    yield ("log", "")
    yield ("log", "Step 1: Even-Paz Division (guarantees 1/n)")
    yield ("log", "")

    allocation = {a.name: [] for a in agent}

    yield from even_paz_recursive(agent, [(0.0, 1.0)], allocation, total_slices, depth=1)
    for ag in agent:
        allocation[ag.name] = merge_intervals(allocation[ag.name])

    yield ("state", allocation, "Even-Paz Division")

    yield ("log", "")
    yield ("log", "\nConrtolled Envy Reduction Phase")
    yield ("log", "\nOnly moves small pieces")

    max_round = 100
    for round_num in range(max_round):
        yield ("log", f"\nEnvy Reduction Round {round_num + 1}")

        envy_relationship = []
        for agent_i in agent:
            val_i = agent_i.get_value_of_bundle(allocation.get(agent_i.name, []), total_slices)
            for agent_j in agent:
                if agent_i.name == agent_j.name:
                    continue
                val_j = agent_i.get_value_of_bundle(allocation.get(agent_j.name, []), total_slices)

                if agent_i.personality == "Greedy":
                    threshold = 0.05
                elif agent_i.personality == "Selfless":
                    threshold = 0.25
                else:
                    threshold = 0.1

                if val_j > val_i + threshold:
                    envy_relationship.append((agent_i, agent_j, val_i, val_j, val_j - val_i))


        if not envy_relationship:
            yield ("log", "NO Significant envy detected - allocation is envy free")
            break

        greedy_agents = [e for e in envy_relationship if e[0].personality == "Greedy"]
        regular_agents = [e for e in envy_relationship if e[0].personality == "Regular"]
        selfless_agents = [e for e in envy_relationship if e[0].personality == "Selfless"]

        envy_relationship = greedy_agents + regular_agents + selfless_agents

        moves_made = 0
        for nv_agent, nv_target, nv_val, target_val, diff in envy_relationship[:3]:
            yield ("log", f"\n{nv_agent.name}{nv_agent.personality} envies {nv_target.name} by {diff:2f}")

            target_piece = allocation.get(nv_target.name, [])
            if not target_piece:
                continue

            best_piece = max(target_piece,
                             key=lambda piece: nv_agent.get_value_of_interval(piece[0], piece[1], total_slices))
            best_value = nv_agent.get_value_of_interval(best_piece[0], best_piece[1], total_slices)

            if nv_agent.personality == "Greedy":
                move_factor = 0.6
                min_value_threshold = 0.02
            elif nv_agent.personality == "Selfless":
                move_factor = 0.25
                min_value_threshold = 0.1
            else:
                move_factor = 0.4
                min_value_threshold = 0.05

            if best_value > 0.5:
                move_amount = min(best_value * move_factor, diff * 0.8)

                start, end = best_piece
                cut_point = find_simple_cut(nv_agent, start, end, move_amount if move_amount < best_value else best_value, total_slices)

                small_piece = (start, cut_point)
                remaining_piece = (cut_point, end)
                small_value = nv_agent.get_value_of_interval(small_piece[0], small_piece[1], total_slices)

                if small_value > min_value_threshold and small_value < best_value * 0.7:
                    target_piece.remove(best_piece)

                    allocation[nv_agent.name].append(small_piece)

                    if remaining_piece[1] - remaining_piece[0] > 0.001:
                        allocation[nv_target.name].append(remaining_piece)

                    allocation[nv_target.name] = merge_intervals(allocation[nv_target.name])
                    allocation[nv_agent.name] = merge_intervals(allocation[nv_agent.name])

                    moves_made += 1
                    yield ("log", f"  Moved [{small_piece[0]:.3f}-{small_piece[1]:.3f}] (value: {small_value:.2f}) from {nv_target.name} to {nv_agent.name}")

                    new_nv_val = nv_agent.get_value_of_bundle(allocation.get(nv_agent.name, []), total_slices)
                    new_target_val = nv_agent.get_value_of_bundle(allocation.get(nv_target.name, []), total_slices)
                    yield ("log", f"{nv_agent.name} now: {new_nv_val:.2f} (was {nv_val:.2f})")

                    yield ("state", allocation, f"Envy reduction: {nv_agent.name} takes from {nv_target.name}")
                else:
                    yield ("log", "Move would be too large or too small - Skipping")
        if moves_made == 0:
            yield ("log", "No usful moves could be made - Skipping")
    yield ("log", "")
    yield from Verify_Results(agent, allocation, total_slices)


def even_paz_recursive(agent, cake_intervals, allocation, total_slices, depth=1):
    n = len(agent)
    indent =  "  " * depth

    if n == 1:
        ag = agent[0]
        for start, end in cake_intervals:
            if end - start > 1e-6:
                allocation[ag.name].append((start, end))
                val = ag.get_value_of_interval(start, end, total_slices)
                yield ("log", f"{indent}{ag.name} gets [{start:.2f} - {end:.2f}] (value: {val:.2f})")
        return

    all_intervals = []
    for start, end in cake_intervals:
        if end - start > 1e-6:
            all_intervals.append([start, end])

    if not all_intervals:
        return

    cut_point = []
    for ag in agent:
        total_val = ag.get_value_of_bundle(all_intervals, total_slices)
        if ag.personality == "Greedy":
            target = total_val * 0.45
        elif ag.personality == "Selfless":
            target = total_val * 0.55
        else:
            target = total_val /2.0

        if target < 0.001:
            cut_point.append(0.5)
            continue

        accumulated = 0.0
        found = False
        for start, end in all_intervals:
            if accumulated >= target:
                break
            low, high = start, end
            for _ in range(40):
                mid = (low + high) / 2.0
                val = ag.get_value_of_interval(start, mid, total_slices)
                if val < target - accumulated:
                    low = mid
                else:
                    high = mid
            cut_point.append(high)
            found = True
            break
        if not found:
            cut_point = [1.0]
    if not cut_point:
        cut_point = [0.5]

    cut_point.sort()

    if any(a.personality == "Greedy" for a in agent):
        median_idx = len(cut_point) // 3
    elif any(a.personality == "Selfless" for a in agent):
        median_idx = len(cut_point) * 2 // 3
    else:
        median_idx = len(cut_point) // 2

    median_cut = cut_point[median_idx]

    left_agents = []
    right_agents = []
    for ag in agent:
        total_val = ag.get_value_of_bundle(all_intervals, total_slices)
        if ag.personality == "Greedy":
            target = total_val * 0.45
        elif ag.personality == "Selfless":
            target = total_val * 0.55
        else:
            target = total_val / 2.0
        if target < 0.001:
            left_agents.append(ag)
            continue

        accumulated = 0.0
        agent_cut = 1.0
        found = False
        for start, end in all_intervals:
            if accumulated >= target:
                agent_cut = start
                found = True
                break
            low, high = start, end
            for _ in range(40):
                mid = (low + high) / 2.0
                val = ag.get_value_of_interval(start, mid, total_slices)
                if val < target - accumulated:
                    low = mid
                else:
                    high = mid
            agent_cut = high
            found = True
            break
        if not found:
            agent_cut = 1.0

        if agent_cut < median_cut:
            left_agents.append(ag)
        else:
            right_agents.append(ag)
    if not left_agents:
        left_agents = [agent[0]]
        right_agents = agent[1:]
    elif not right_agents:
        left_agents = agent[:-1]
        right_agents = [agent[-1]]

    left_cake = []
    right_cake = []
    for start, end in all_intervals:
        if end <= median_cut + 1e-6:
            left_cake.append((start, end))
        elif start >= median_cut - 1e-6:
            right_cake.append((start, end))
        else:
            if median_cut - start > 1e-6:
                left_cake.append((start, median_cut))
            if end - median_cut > 1e-6:
                right_cake.append((median_cut, end))

    yield ("log", f"{indent}Median cut at: {median_cut:.3f}")
    yield ("log", f"{indent}Left agents: {[a.name for a in left_agents]}")
    yield ("log", f"{indent}Right agents: {[a.name for a in right_agents]}")

    if left_agents and left_cake:
        yield from even_paz_recursive(left_agents, left_cake, allocation, total_slices, depth=depth+1)
    if right_agents and right_cake:
        yield from even_paz_recursive(right_agents, right_cake, allocation, total_slices, depth=depth+1)

def maximum_utilitarian_allocation(agents, total_slices):
    allocation = {agent.name:[] for agent in agents}

    for slice_idx in range(total_slices):
        slice_start = float(slice_idx) / total_slices
        slice_end = float(slice_idx + 1) / total_slices

        best_agent = None
        best_value = -1
        for agent in agents:
            value = agent.get_value_of_interval(slice_start, slice_end, total_slices)
            if value > best_value:
                best_value = value
                best_agent = agent
        if best_agent:
            allocation[best_agent.name].append((slice_start, slice_end))

    for agent in agents:
        allocation[agent.name] = merge_intervals(allocation[agent.name])
    return allocation

def count_envy_for_allocation(agents, allocation, total_slices):
    envy_count = 0
    for agent_i in agents:
        i_val = agent_i.get_value_of_bundle(allocation.get(agent_i.name, []), total_slices)

        for agent_j in agents:
            if agent_j.name == agent_i.name:
                continue
            j_val = agent_i.get_value_of_bundle(allocation.get(agent_j.name, []), total_slices)

            if j_val > i_val + 1:
                envy_count += 1
    return envy_count


#verify that the calculation is envy-free
def Verify_Results(agents, allocation, total_slices):
    for agent in agents:
        if agent.name in allocation:
            allocation[agent.name] = merge_intervals(allocation[agent.name])

    yield from log_final_matrix(agents, allocation, total_slices)
    yield from verify_proportional(agents, allocation, total_slices)
    yield from verify_envy_free(agents, allocation, total_slices)

def log_final_matrix(agents, allocation, total_slices):
    yield ("log", "")
    yield ("log", "Final Allocation")
    yield ("log", "")

    for agent in agents:
        intervals = allocation.get(agent.name, [])
        val = agent.get_value_of_bundle(intervals, total_slices)
        intervals_str = ", ".join([f"[{s:.3f}-{e:.3f}]" for s, e in intervals if abs(e - s) > 0.001])
        cake_percent = sum(e - s for s, e in intervals) * 100
        yield ("log", f"{agent.name:10}: Values{val:6.2f} || Cake={cake_percent:5.1f}% || {intervals_str}")

def verify_proportional(agents, allocation, total_slices):
    n = len(agents)
    fair_share = 100/n

    yield ("log", "")
    yield ("log", "Proportional Verification")
    yield ("log", "")
    Proportional = True
    for agent in agents:
        val = agent.get_value_of_bundle(allocation.get(agent.name, []), total_slices)
        if val < fair_share - 0.1:
            Proportional = False
            yield ("log", f"(NO) {agent.name}: {val:.2f} < {fair_share:.2f}")
        else:
            yield ("log", f"(YES) {agent.name}: {val:.2f} >= {fair_share:.2f}")

    if Proportional:
        yield ("log", "\nAll Player Got at least 1/n")
    else :
        yield ("log", "\nNot All Player Got at least 1/n")

def verify_envy_free(agents, allocation, total_slices):
    yield ("log", "")
    yield ("log", "Envy Freeness verification")
    yield ("log", "")

    envy_free = True
    envy_count = 0
    for agent_i in agents:
        i_val = agent_i.get_value_of_bundle(allocation.get(agent_i.name, []), total_slices)

        for agent_j in agents:
            if agent_j.name == agent_i.name:
                continue
            j_val = agent_i.get_value_of_bundle(allocation.get(agent_j.name, []), total_slices)

            if j_val > i_val + 0.1:
                envy_free = False
                envy_count = envy_count + 1
                yield ("log", f"(NO) {agent_i.name} envies {agent_j.name} ({i_val:.2f} < {j_val:.2f})")
            else:
                yield ("log", f"(YES) {agent_i.name} does not envy {agent_j.name} ({i_val:.2f} => {j_val:.2f})")

        if envy_free:
            yield ("log", "")
            yield ("log", "(YES) Allocation is envy-free")
            yield ("log", "")
        else :
            yield ("log", "")
            yield ("log", f"(NO) Allocation is not envy-free, there is {envy_count} envy counts amount the players")
            yield ("log", "")
    return envy_free


#create the GUI
class CakeUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Fair Division")
        self.root.geometry("1300x900")

        self.main_frame = tk.Frame(self.root, bg="#f8f9fa")
        self.main_frame.pack(fill="both", expand=True)

        self.colors = ["#ff4d4d", "#4da6ff", "#5cd65c", "#cd6faf", "#ffb366", "#9966ff", "#f66b2e", "#66ccff"]
        self.show_main_menu()

        self.current_allocation = {}
        self.active_agents = []
        self.utilitarian_allocation = {}
        self.utilitarian_welfare = {}

    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def generate_random_values(self, entry_widget, personality="Regular"):
        if personality == "Greedy":
            peak = random.randint(1, self.s_count - 2)
            values = []
            for i in range(self.s_count):
                distance = abs(i - peak)
                value = max(1, 100 - (distance * 1.5))
                values.append(value)
            total = sum(values)
            values = [int(v * 100 / total) for v in values]
            diff = 100 - sum(values)
            values[-1] += diff
        elif personality == "Selfless":
            base = 100 // self.s_count
            values = [base] * self.s_count
            remainder = 100 % self.s_count
            for i in range(remainder):
                values[i] += 1
            for i in range(len(values)):
                variation = random.randint(-2, 2)
                values[i] = max(1, values[i] + variation)
            total = sum(values)
            if total != 100:
                values[-1] += (100 - total)
        else:
            cuts = sorted([random.randint(0, 100) for _ in range(self.s_count - 1)])
            values = []
            prev = 0
            for c in cuts:
                values.append(c - prev)
                prev = c
            values.append(100 - prev)

        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, " ".join(map(str, values)))

    def show_main_menu(self):
        self.clear_frame()
        container = tk.Frame(self.main_frame, bg="#f8f9fa", bd=2, relief="solid", padx=40, pady=35)
        container.pack(expand=True)

        tk.Label(container, text="Fair Division Showcase", font=("Helvetica", 18, "bold"), bg="#ffffff",
                 fg="#212529").pack(pady=(0, 10))

        tk.Label(container, text="2 Players: I Cut You Choose", font=("Helvetica", 10, "bold"), bg="#ffffff",
                 fg="#212529").pack(pady=(0, 10))
        tk.Label(container, text="3 Players: Selfridge-Conway", font=("Helvetica", 10, "bold"), bg="#ffffff",
                 fg="#212529").pack(pady=(0, 10))
        tk.Label(container, text="4 Players: Even-Paz", font=("Helvetica", 10, "bold"), bg="#ffffff",
                 fg="#212529").pack(pady=(0, 10))

        input_grid = tk.Frame(container, bg="#ffffff")
        input_grid.pack(pady = 10)

        tk.Label(input_grid, text="Number of Players (2-8):", font=("Helvetica", 11, "bold"), bg="#ffffff",
                 fg="#212529").grid(row=0, column=0, padx=10, pady=8)
        self.player_input = tk.Entry(input_grid, font=("Helvetica", 11), width=8, justify="center")
        self.player_input.grid(row=0, column=1, padx=10, pady=8)

        tk.Label(input_grid, text="Number of Slices:", font=("Helvetica", 11, "bold"), bg="#ffffff",
                 fg="#212529").grid(row=1, column=0, padx=10, pady=8)
        self.slices_input = tk.Entry(input_grid, font=("Helvetica", 11), width=8, justify="center")
        self.slices_input.grid(row=1, column=1, padx=10, pady=8)

        submit_btn = tk.Button(input_grid, text="Submit", font=("Helvetica", 11, "bold"), bg="#ffffff", fg="#212529",
                               padx=25, pady=8, command=self.menu_submission)
        submit_btn.grid(row=2, column=0, pady=15)

    def menu_submission(self):
        try:
            p_count = int(self.player_input.get().strip())
            s_count = int(self.slices_input.get().strip())
            if p_count < 2 or p_count > 8:
                raise ValueError("Players must be 2-8")
            if s_count <= 1:
                raise ValueError("Slices must be greater than 1")
            if s_count > 100:
                raise ValueError("Slices must equal to or less than 100")
        except ValueError as e:
            messagebox.showerror("Error in Inputs", str(e))
            return

        self.build_showcase_page(p_count, s_count)

    def build_showcase_page(self, p_count, s_count):
        self.clear_frame()
        self.s_count = s_count
        self.p_count = p_count

        top_panel = tk.Frame(self.main_frame, bg="#ffffff", bd=1, relief="solid")
        top_panel.pack(side="top", fill="x", padx=10, pady=5)

        if p_count == 2:
            algorithm = "I-Cut-You-Choose"
            algorithm_color = "#28a745"
        elif p_count == 3:
            algorithm = "Selfridge-Conway"
            algorithm_color = "#28a745"
        else:
            algorithm = "Even-Paz"
            algorithm_color = "#28a745"

        tk.Label(top_panel, text=f"{algorithm} ({p_count} Players)", font=("Helvetica", 12, "bold"), bg="#ffffff",
                 fg=algorithm_color).pack(anchor="w", padx=15, pady=6)
        tk.Label(top_panel, text="Edit Preference Vectors (must Sum to 100):", font=("Helvetica", 10), bg="#ffffff",
                 fg="#212529").pack(anchor="w", padx=15, pady=2)

        grid_frame = tk.Frame(top_panel, bg="#ffffff")
        grid_frame.pack(fill="x", padx=15, pady=5)

        self.name_entries = []
        self.values_entries = []
        self.personality_entries = []
        placeholder_names = ["Andrea", "Ian", "Scott", "Liam", "Holly", "Keir", "Harry", "Grace"]

        canvas = tk.Canvas(grid_frame, bg="#ffffff", height=200)
        scrollbar = tk.Scrollbar(grid_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#ffffff")

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for i in range(p_count):
            color = self.colors[i % len(self.colors)]
            row_frame = tk.Frame(scrollable_frame, bg="#ffffff")
            row_frame.pack(fill="x", pady=2)

            color_box = tk.Frame(row_frame, bg=color, width=16, height=16)
            color_box.pack(side="left", padx=(0, 6))
            color_box.pack_propagate(False)

            name_entry = tk.Entry(row_frame, width=10, font=("Helvetica", 9, "bold"))
            name_entry.insert(0, placeholder_names[i] if i < len(placeholder_names) else f"P{i + 1}")
            name_entry.pack(side="left", padx=5)
            self.name_entries.append(name_entry)

            personality_var = tk.StringVar(value="Regular")
            personality_menu = tk.OptionMenu(row_frame, personality_var, "Greedy", "Regular", "Selfless")
            personality_menu.config(width=8, font=("Helvetica", 8))
            personality_menu.pack(side="left", padx=5)
            self.personality_entries.append(personality_var)

            base_val = 100 // s_count
            remainder = 100 % s_count
            default_vals = [base_val + (1 if r < remainder else 0) for r in range(s_count)]

            value_entry = tk.Entry(row_frame, width=75, font=("Helvetica", 10))
            value_entry.insert(0, " ".join(map(str, default_vals)))
            value_entry.pack(side="left", padx=10)
            self.values_entries.append(value_entry)

            random_btn = tk.Button(row_frame, text="Random", font=("Helvetica", 8, "bold"), bg="#28a745", fg="#ffffff",
                                   padx=5, pady=2, bd=0, command=lambda e=value_entry, p=personality_var: self.generate_random_values(e))
            random_btn.pack(side="left", pady=5)

        body_frame = tk.Frame(self.main_frame, bg="#f8f9fa")
        body_frame.pack(side="top", fill="both", expand=True, padx=10, pady=5)

        left_panel = tk.Frame(body_frame, bg="#f8f9fa", bd=1, relief="solid")
        left_panel.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        self.cake_canvas = tk.Canvas(left_panel, bg="#ffffff", highlightthickness=0)
        self.cake_canvas.pack(fill="both", expand=True, padx=15, pady=15)

        self.control_bar = tk.Frame(left_panel, bg="#ffffff")
        self.control_bar.pack(side="bottom", fill="x", pady=10)

        self.start_btn = tk.Button(self.control_bar, text="Start Algorithm", bg="#ad3121", fg="#ffffff", bd=0,
                                   font=("Arial", 11, "bold"), padx=15, pady=6, command=self.start_algorithm)
        self.start_btn.pack(side="left", padx=10)

        self.back_btn = tk.Button(self.control_bar, text="Main Menu", bg="#ad3121", fg="#ffffff", bd=0,
                                  font=("Arial", 10, "bold"), padx=12, pady=5, command=self.show_main_menu)
        self.back_btn.pack(side="left", padx=10)

        self.step_speed_var = tk.DoubleVar(value=100)
        speed_frame = tk.Frame(self.control_bar, bg="#f8f9fa")
        speed_frame.pack(side="right", padx=10)
        tk.Label(speed_frame, text="Speed", font=("Arial", 9), bg="#ffffff").pack(side="left")
        tk.Scale(speed_frame, from_=50, to=2000, orient="horizontal", variable=self.step_speed_var, length=100,
                 bg="#f8f9fa").pack(side="left")

        right_panel = tk.Frame(body_frame, bg="#f8f9fa", width=500, bd=1, relief="solid")
        right_panel.pack(side="right", fill="both", padx=5, pady=5)
        right_panel.pack_propagate(False)

        tk.Label(right_panel, text="Algorithm Process", font=("Arial", 11, "bold"), bg="#1e1e1e", fg="#00ff00",
                 pady=4).pack(side="top", fill="x")

        self.log_text = tk.Text(right_panel, bg="#151515", fg="#d4d4d4", font=("Consolas", 9), state="disabled",
                                wrap="word", width=60, height=20)
        self.log_text.pack(fill="both", expand=True)
        self.root.update()
        self.reset_visual_cake_state()

    def reset_visual_cake_state(self):
        if hasattr(self, "active_agents") and self.active_agents:
            pass
        else:
            try:
                temp_agent =[]
                for i in range(self.p_count):
                    name = self.name_entries[i].get().strip() or f"p{i+1}"
                    values = [float(v) for v in self.values_entries[i].get().split()]
                    if len(values) == self.s_count and abs(sum(values) - 100) < 0.5:
                        temp_agent.append(Agent(name, values))
                if len(temp_agent) == self.p_count:
                    self.active_agents = temp_agent
            except (ValueError, AttributeError) as e:
                messagebox.showerror("Error", e)


        self.current_allocation = {name_entry.get().strip() or f"P{i + 1}": [] for i, name_entry in
                                   enumerate(self.name_entries)}
        self.draw_visual_cake_state()

    def draw_visual_cake_state(self):
        print(f"Drawing cake with allocation: {self.current_allocation}")
        self.cake_canvas.delete("all")
        w, h = self.cake_canvas.winfo_width(), self.cake_canvas.winfo_height()
        cx, cy = w // 2, h // 2
        cx = cx - 60
        radius = min(cx, cy) - 35
        if radius < 40:
            radius = 120

        self.cake_canvas.create_oval(cx - radius, cy - radius, cx + radius, cy + radius, fill="#e9ecef",
                                     outline="#565657", width=2)

        for p_idx, name_entry in enumerate(self.name_entries):
            p_name = name_entry.get().strip() or f"P{p_idx + 1}"
            intervals = self.current_allocation.get(p_name, [])
            color = self.colors[p_idx % len(self.colors)]

            for start, end in intervals:
                if abs(end - start) < 0.001:
                    continue
                start_angle = start * 360.0
                slice_size = (end - start) * 360.0

                self.cake_canvas.create_arc(cx - radius, cy - radius, cx + radius, cy + radius, start=start_angle,
                                            extent=slice_size, fill=color, outline="#ffffff", width=1)

        for i in range(self.s_count):
            angle = (i / self.s_count) * 360.0
            rad = math.radians(angle)
            x = cx + (radius + 18) * math.cos(rad)
            y = cy - (radius + 18) * math.sin(rad)
            self.cake_canvas.create_text(x, y, text=str(i), font=("Arial", 10, 'bold'), fill="#16A6A4")

        lx, ly = cx + radius + 30, cy - radius

        player_values = {}
        player_percentages = {}
        agent_dict = {agent.name: agent for agent in self.active_agents} if hasattr(self, "active_agents") and self.active_agents else {}

        for p_idx, name_entry in enumerate(self.name_entries):
            p_name = name_entry.get().strip() or f"P{p_idx + 1}"
            intervals = self.current_allocation.get(p_name, [])
            cake_percent = sum(e-s for s, e in intervals) * 100
            agent = agent_dict.get(p_name)
            if agent:
                val = agent.get_value_of_bundle(intervals, self.s_count)
                player_values[p_name] = val
            else:
                if p_idx < len(self.name_entries):
                    agent = self.active_agents[p_idx]
                    val = agent.get_value_of_bundle(intervals, self.s_count)
                    player_values[p_name] = val
                else:
                    player_values[p_name] = 0.0
            player_percentages[p_name] = cake_percent

        num_players = len(self.name_entries)
        legend_height = num_players * 28
        legend_start_y = (h - legend_height) // 2


        for p_idx, name_entry in enumerate(self.name_entries):
            p_name = name_entry.get().strip() or f"P{p_idx + 1}"
            color = self.colors[p_idx % len(self.colors)]
            player_val = player_values.get(p_name, 0.0)
            cake_percent = player_percentages.get(p_name, 0.0)

            y_pos = legend_start_y + p_idx * 28
            self.cake_canvas.create_rectangle(lx, y_pos, lx + 20, y_pos + 15, fill=color,
                                              outline="")
            self.cake_canvas.create_text(lx + 25, y_pos + 8, text=f"{p_name}- values: {player_val:.2f} (Cake: {cake_percent:.1f}%)", font=("Arial", 7), anchor="w",
                                         fill="#16A6A4")

    def append_log(self, text):
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, text + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")

    def start_algorithm(self):
        try:
            self.active_agents = []
            for i in range(self.p_count):
                name = self.name_entries[i].get().strip() or f"P{i + 1}"
                personality = self.personality_entries[i].get() if i < len(self.personality_entries) else "Regular"
                values = [float(v) for v in self.values_entries[i].get().split()]
                if len(values) != self.s_count:
                    raise ValueError(
                        f"Inconsistent number of values for {name}, Expected {self.s_count} got {len(values)}")
                if abs(sum(values) - 100) > 0.5:  # this is for rounding errors
                    raise ValueError(f"Inconsistent number of values for {name}, Expected 100 got {sum(values)}")
                self.active_agents.append(Agent(name, values, personality))
                print(f"Agent Active: {[a.name for a in self.active_agents]} ")
        except Exception as ex:
            messagebox.showerror("Error", str(ex))
            return

        self.root.after(1000, self.run_maximum_util_background)

        self.start_btn.config(state="disabled", text="Running")
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", tk.END)
        self.log_text.config(state="disabled")

        self.reset_visual_cake_state()

        if self.p_count == 2:
            self.generator = ICutUChoose(self.active_agents, self.s_count)
        elif self.p_count == 3:
            self.generator = Selfridge_Conway(self.active_agents, self.s_count)
        else:
            self.generator = Even_Paz(self.active_agents, self.s_count)

        self.step_by_step()

    def run_maximum_util_background(self):
        try:
            agents = self.active_agents
            total_slices = self.s_count

            if not agents:
                return
            self.utilitarian_allocation = maximum_utilitarian_allocation(agents, total_slices)

            self.utilitarian_welfare = self.calculate_welfare_metrics(agents, self.utilitarian_allocation, total_slices)

            print(f"slice-based utilitarian: {self.utilitarian_welfare['utilitarian']}")
        except Exception as ex:
            messagebox.showerror("Error", str(ex))



    def calculate_welfare_metrics(self, agents, allocation, total_slices):
        valuation = {}
        for agent in agents:
            intervals = allocation.get(agent.name, [])
            val = agent.get_value_of_bundle(intervals, total_slices)
            valuation[agent.name] = val / 100.0

        vals_list = list(valuation.values())
        utilitarian_score = sum(vals_list)
        egalitarian_score = min(vals_list) if vals_list else 0

        nash_score = 1.000
        for v in vals_list:
            nash_score *= v

        if len(vals_list) > 0:
            display_nash_score = nash_score ** (1.0/len(vals_list))
        else:
            display_nash_score = 0.0

        return{'utilitarian': utilitarian_score, 'egalitarian': egalitarian_score, 'nash': display_nash_score, 'individual': valuation}

    def step_by_step(self):
        try:
            step = next(self.generator)
            if step[0] == "log":
                self.append_log(step[1])
                self.root.after(int(self.step_speed_var.get()), self.step_by_step)
            elif step[0] == "state":
                self.current_allocation = copy.deepcopy(step[1])
                self.append_log(f"\n>> [Update]: {step[2]}")
                self.draw_visual_cake_state()
                self.root.after(int(self.step_speed_var.get()), self.step_by_step)
        except StopIteration:
            if self.p_count == 2:
                algorithm = "I-Cut-You-Choose"
                msg = f"{algorithm} Complete!"
            elif self.p_count == 3:
                algorithm = "Selfridge_Conway"
                msg = f"{algorithm} Complete!"
            else:
                algorithm = "Even_Paz"
                msg = f"{algorithm} Complete!"
            message = messagebox.showinfo("Complete", msg)
            self.start_btn.config(state="normal", text="Start Algorithm")
            if hasattr(self, 'welfare_btn') and self.welfare_btn:
                self.welfare_btn.destroy()
            self.welfare_btn = tk.Button(self.control_bar, text="View Welfare Metrics", bg="#28a746", fg="white",
                                         font=("Arial", 10, "bold"), padx=10, pady=5, command=self.show_welfare_metrics)
            self.welfare_btn.pack(side="left", padx=10)

    def show_welfare_metrics(self):
        envy_free_welfare = self.calculate_welfare_metrics(self.active_agents, self.current_allocation, self.s_count)


        has_utilitarian = hasattr(self, "utilitarian_allocation") and self.utilitarian_allocation
        utilitarian_envy_count = count_envy_for_allocation(self.active_agents, self.utilitarian_allocation, self.s_count)
        envy_free_envy_count = count_envy_for_allocation(self.active_agents, self.current_allocation, self.s_count)
        pop_win = tk.Toplevel(self.root)
        pop_win.title("Social Welfare Scores")
        pop_win.geometry("850x1000")
        pop_win.configure(bg="#ffffff")
        pop_win.resizable(False, False)

        header = tk.Frame(pop_win, bg="#be8bf0", pady=12)
        header.pack(fill="x")
        tk.Label(header, text="Welfare Statistics", font=("Helvetica", 14, "bold"), fg="white", bg="#be8bf0").pack()
        tk.Label(header, text="Envy-free algorithm Vs Maximum Utilitarian Allocation", font=("Helvetica", 9), fg="white", bg="#be8bf0").pack()

        main_frame = tk.Frame(pop_win, bg="#ffffff", padx=20, pady=15)
        main_frame.pack(fill="both", expand=True)

        def add_welfare_scores(parent, label, score_value, color):
            row = tk.Frame(parent, bg="#ffffff", pady=2)
            row.pack(fill="x")

            lbl_title = tk.Label(row, text=f"{label}:", font=("Helvetica", 9, "bold"), fg="#333333", width=15, anchor="w", bg="#ffffff")
            lbl_title.pack(side="left")

            lbl_val = tk.Label(row, text=f"{score_value:.4f}", font=("Helvetica", 9, "bold"), fg=color, bg="#f8f9fa", width=12, bd=1, relief="solid")
            lbl_val.pack(side="left", padx=5)

        envy_frame = tk.LabelFrame(main_frame, text="Envy-Free Algorithm", font=("Helvetica", 11, "bold"), fg="#ffffff", bg = "#be8bf0", padx=10, pady=10)
        envy_frame.pack(fill="x", pady=5)

        add_welfare_scores(envy_frame, "Utilitarian", envy_free_welfare['utilitarian'], "#a10202")
        add_welfare_scores(envy_frame, "Egalitarian", envy_free_welfare['egalitarian'], "#69d671")
        add_welfare_scores(envy_frame, "Nash Score", envy_free_welfare['nash'], "#a677d1")

        tk.Label(envy_frame, text="Individual Player Values", font=("Helvetica", 11, "bold"), bg="#ffffff", fg="#333333").pack(anchor="w", pady=(5, 0))
        for agent_name, value in envy_free_welfare['individual'].items():
            tk.Label(envy_frame, text=f" {agent_name}: {value:.2f}", font=("Helvetica", 8), bg="white", fg="#555555").pack(anchor="w")

        if has_utilitarian:
            util_frame = tk.LabelFrame(main_frame, text="Maximum Utilitarian", font=("Helvetica", 11, "bold"),
                                       fg="#ffffff", bg="#be8bf0", padx=10, pady=10)
            util_frame.pack(fill="x", pady=5)

            add_welfare_scores(util_frame, "Utilitarian", self.utilitarian_welfare['utilitarian'], "#a10202")
            add_welfare_scores(util_frame, "Egalitarian", self.utilitarian_welfare['egalitarian'], "#69d671")
            add_welfare_scores(util_frame, "Nash Score", self.utilitarian_welfare['nash'], "#a677d1")

            tk.Label(util_frame, text="Individual Player Values", font=("Helvetica", 11, "bold"), bg="#ffffff",
                     fg="#333333").pack(anchor="w", pady=(5, 0))
            for agent_name, value in self.utilitarian_welfare['individual'].items():
                tk.Label(util_frame, text=f" {agent_name}: {value:.2f}", font=("Helvetica", 8), bg="white",
                         fg="#555555").pack(anchor="w")

            comp_frame = tk.LabelFrame(main_frame, text="Comparator", font=("Helvetica", 11, "bold"),fg="#ff0000", bg="#be8bf0", padx=10, pady=10)
            comp_frame.pack(fill="x", pady=5)

            util_diff = self.utilitarian_welfare['utilitarian'] - envy_free_welfare['utilitarian']
            egal_diff = self.utilitarian_welfare['egalitarian'] - envy_free_welfare['egalitarian']
            nash_diff = self.utilitarian_welfare['nash'] - envy_free_welfare['nash']

            tk.Label(comp_frame, text="Maximum Utilitarian - Envy-Free", font=("Helvetica", 9, "bold"), bg="#ffffff", fg="#333333").pack(anchor="w")

            def add_diff_label(parent, label, diff):
                sign = "+" if diff >= 0 else ""
                color = "#28a745" if diff > 0 else "#ff0000" if diff < 0 else "#666666"
                tk.Label(parent, text=f" {label}:{sign}{diff:.2f}", font=("Helvetica", 9), bg="#ffffff", fg=color).pack(anchor="w")

            add_diff_label(comp_frame, "Utilitarian", util_diff)
            add_diff_label(comp_frame, "Egalitarian", egal_diff)
            add_diff_label(comp_frame, "Nash Score", nash_diff)
            tk.Label(comp_frame, text=f"Envy-Freeness Envy Count: {envy_free_envy_count}", font=("Helvetica", 9),bg="#ffffff", fg="#333333").pack(anchor="w")
            tk.Label(comp_frame, text=f"Maximum Utilitarian Envy Count: {utilitarian_envy_count}", font=("Helvetica", 9),bg="#ffffff", fg="#333333").pack(anchor="w")

        btn_close = tk.Button(main_frame, text="Close", bg="#ff0000", fg="#333333", font=("Arial", 9, "bold"), padx=10, pady=10, bd=0, command=pop_win.destroy)
        btn_close.pack(side="bottom", anchor="w", pady=10)










if __name__ == "__main__":
    root = tk.Tk()
    app = CakeUI(root)
    root.mainloop()
