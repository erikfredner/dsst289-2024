import re
import sys

def process_qmd(input_path, output_path):
    """
    Processes a Quarto Markdown (.qmd) file by:
    1. Changing `echo: false` to `echo: true` in the YAML metadata block.
    2. Blanking out content in code chunks labeled as questions (e.g., {r, question-01}),
       but preserving lines that start with `#|`.
    3. Replacing content inside ::: {.answer} divs with "Your answer here."

    Args:
        input_path (str): Path to the input .qmd file.
        output_path (str): Path to save the modified .qmd file.
    """
    # Regular expressions to identify code chunks and answer divs
    question_chunk_start_pattern = re.compile(r'^```{r\s*,\s*question-\d+.*}$', re.IGNORECASE)
    code_chunk_end_pattern = re.compile(r'^```$')

    # Enhanced regex patterns for answer divs with flexible whitespace
    answer_div_start_pattern = re.compile(r'^:::\s*\{\.answer\}\s*$', re.IGNORECASE)
    answer_div_end_pattern = re.compile(r'^:::\s*$', re.IGNORECASE)

    # Regex pattern to find 'echo: false' with optional whitespace
    echo_false_pattern = re.compile(r'^echo\s*:\s*false\s*$', re.IGNORECASE)
    echo_true_line = 'echo: true\n'

    in_yaml = False  # Flag to track if we're inside the YAML metadata block

    with open(input_path, 'r', encoding='utf-8') as infile, \
         open(output_path, 'w', encoding='utf-8') as outfile:

        for line in infile:
            stripped_line = line.strip()

            # Check for the start or end of YAML metadata block
            if stripped_line == '---':
                in_yaml = not in_yaml  # Toggle the YAML flag
                outfile.write(line)    # Write the delimiter line
                continue  # Move to the next line

            # If inside YAML, look for 'echo: false' and replace it
            if in_yaml:
                if echo_false_pattern.match(stripped_line):
                    outfile.write(echo_true_line)
                else:
                    outfile.write(line)
                continue  # Move to the next line

            # Handle question code chunks
            if question_chunk_start_pattern.match(stripped_line):
                outfile.write(line)  # Write the opening ```{r, question-XX}
                # Now process all lines until closing ```
                while True:
                    next_line = infile.readline()
                    if not next_line:
                        break  # End of File
                    if code_chunk_end_pattern.match(next_line.strip()):
                        outfile.write('```\n')  # Write the closing ```
                        break  # Found the closing ```
                    elif next_line.strip().startswith('#|'):
                        outfile.write(next_line)  # Write the option line
                    # Else, skip the line (don't write it)
                continue  # Move to the next line

            # Handle answer divs
            if answer_div_start_pattern.match(stripped_line):
                outfile.write(line)  # Write the opening ::: {.answer}
                outfile.write('Your answer here.\n')  # Insert placeholder
                # Now skip all lines until closing :::
                while True:
                    next_line = infile.readline()
                    if not next_line:
                        break  # End of File
                    if answer_div_end_pattern.match(next_line.strip()):
                        outfile.write(':::\n')  # Write the closing :::
                        break
                continue  # Move to the next line

            # For all other lines, write them as-is
            outfile.write(line)

    print(f"Processing complete. Modified file saved as '{output_path}'.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python process_qmd.py input.qmd output.qmd")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    process_qmd(input_file, output_file)
