import argparse
import sys

from cspuz import Solver, graph
from cspuz.puzzle import util
from cspuz.constraints import count_true
from cspuz.generator import generate_problem, count_non_default_values, Choice


def solve_gokigen(height, width, problem):
    solver = Solver()
    edge_type = solver.bool_array((height, width))  # false: /, true: \
    solver.add_answer_key(edge_type)

    g = graph.Graph((height + 1) * (width + 1))
    edge_list = []
    for y in range(height):
        for x in range(width):
            g.add_edge(y * (width + 1) + x, (y + 1) * (width + 1) + (x + 1))
            edge_list.append(edge_type[y, x])
            g.add_edge(y * (width + 1) + (x + 1), (y + 1) * (width + 1) + x)
            edge_list.append(~edge_type[y, x])
    graph.active_edges_acyclic(solver, edge_list, g)

    for y in range(height + 1):
        for x in range(width + 1):
            if problem[y][x] >= 0:
                related = []
                if 0 < y and 0 < x:
                    related.append(edge_type[y - 1, x - 1])
                if 0 < y and x < width:
                    related.append(~edge_type[y - 1, x])
                if y < height and 0 < x:
                    related.append(~edge_type[y, x - 1])
                if y < height and x < width:
                    related.append(edge_type[y, x])
                solver.ensure(count_true(related) == problem[y][x])

    is_sat = solver.solve()
    return is_sat, edge_type


def generate_gokigen(height, width, no_easy=False, no_adjacent=False, verbose=False):
    pattern = []
    for y in range(height + 1):
        row = []
        for x in range(width + 1):
            lim = (1 if y in (0, height) else 2) * (1 if x in (0, width) else 2)
            row.append(
                Choice(
                    [-1] + list(range(1 if no_easy else 0, lim if no_easy else (lim + 1))),
                    default=-1,
                )
            )
        pattern.append(row)

    def pretest(problem):
        for y in range(height + 1):
            for x in range(width + 1):
                if no_adjacent:
                    if y < height:
                        if problem[y][x] != -1 and problem[y + 1][x] != -1:
                            return False
                    if x < width:
                        if problem[y][x] != -1 and problem[y][x + 1] != -1:
                            return False
                if no_easy:
                    if y < height:
                        if problem[y][x] in (1, 3) and problem[y + 1][x] in (1, 3):
                            return False
                    if x < width:
                        if problem[y][x] in (1, 3) and problem[y][x + 1] in (1, 3):
                            return False
                    if y < height - 1:
                        if (
                            problem[y][x] != -1
                            and problem[y + 1][x] != -1
                            and problem[y + 2][x] != -1
                        ):
                            return False
                    if x < width - 1:
                        if (
                            problem[y][x] != -1
                            and problem[y][x + 1] != -1
                            and problem[y][x + 2] != -1
                        ):
                            return False
        return True

    generated = generate_problem(
        lambda problem: solve_gokigen(height, width, problem),
        builder_pattern=pattern,
        clue_penalty=lambda problem: count_non_default_values(problem, default=-1, weight=2),
        pretest=pretest,
        verbose=verbose,
    )
    return generated


def _main():
    if len(sys.argv) == 1:
        # https://puzsq.sakura.ne.jp/main/puzzle_play.php?pid=7862
        height = 7
        width = 7
        # fmt: off
        problem = [
            [-1, -1, -1, -1, -1, -1, -1, -1],  # noqa: E201, E241
            [-1,  3, -1,  2,  3, -1,  3, -1],  # noqa: E201, E241
            [-1, -1,  1, -1, -1,  1, -1, -1],  # noqa: E201, E241
            [-1, -1, -1, -1,  3,  2, -1, -1],  # noqa: E201, E241
            [-1,  3, -1,  3,  2, -1,  3, -1],  # noqa: E201, E241
            [-1, -1,  1, -1, -1,  1, -1, -1],  # noqa: E201, E241
            [-1,  3, -1, -1,  3, -1,  3, -1],  # noqa: E201, E241
            [-1, -1, -1, -1, -1, -1, -1, -1],  # noqa: E201, E241
        ]
        # fmt: on
        is_sat, ans = solve_gokigen(height, width, problem)
        print("has answer:", is_sat)
        if is_sat:
            print(util.stringify_array(ans, {None: ".", True: "\\", False: "/"}))
    else:
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument("-h", "--height", type=int, required=True)
        parser.add_argument("-w", "--width", type=int, required=True)
        parser.add_argument("--no-easy", action="store_true")
        parser.add_argument("--no-adjacent", action="store_true")
        parser.add_argument("-v", "--verbose", action="store_true")
        args = parser.parse_args()
        height = args.height
        width = args.width
        no_easy = args.no_easy
        no_adjacent = args.no_adjacent
        verbose = args.verbose
        while True:
            problem = generate_gokigen(
                height, width, no_easy=no_easy, no_adjacent=no_adjacent, verbose=verbose
            )
            if problem is not None:
                print(
                    util.stringify_array(problem, lambda x: "." if x == -1 else str(x)), flush=True
                )
                print(flush=True)


if __name__ == "__main__":
    _main()
