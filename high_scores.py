def highscores(self):
    with open("scores.txt", "r") as file:
        lines = file.readlines()
    
    def get_first_number(line):
        match = re.search(r'\d+', line)
        return float(match.group()) if match else float("inf")
    
    sorted_lines = sorted(lines, key=get_first_number, reverse=True)

    with open("scores.txt", "w") as file:
        file.writelines(sorted_lines)
