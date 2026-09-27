# [H] Python code execution sandbox escape in non-docker version in Auto-GPT

## Summary
Severity: High
Advisory: CVE-2023-37274
Aliases: GHSA-5h38-mgp9-rj5f
CVSS: 7.5 (CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:C/C:H/I:H/A:H)
Published: 2023-07-13
Source: https://osv.dev/vulnerability/CVE-2023-37274
Type: osv

## Details
Auto-GPT is an experimental open-source application showcasing the capabilities of the GPT-4 language model. When Auto-GPT is executed directly on the host system via the provided run.sh or run.bat files, custom Python code execution is sandboxed using a temporary dedicated docker container which should not have access to any files outside of the Auto-GPT workspace directory.
Before v0.4.3, the `execute_python_code` command (introduced in v0.4.1) does not sanitize the `basename` arg before writing LLM-supplied code to a file with an LLM-supplied name. This allows for a path traversal attack that can overwrite any .py file outside the workspace directory by specifying a `basename` such as `../../../main.py`. This can further be abused to achieve arbitrary code execution on the host running Auto-GPT by e.g. overwriting autogpt/main.py which will be executed outside of the docker environment meant to sandbox custom python code execution the next time Auto-GPT is started. The issue has been patched in version 0.4.3. As a workaround, the risk introduced by this vulnerability can be remediated by running Auto-GPT in a virtual machine, or another environment in which damage to files or corruption of the program is not a critical problem.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/37xxx/CVE-2023-37274.json
- https://github.com/Significant-Gravitas/Auto-GPT/security/advisories/GHSA-5h38-mgp9-rj5f
- https://nvd.nist.gov/vuln/detail/CVE-2023-37274
- https://github.com/Significant-Gravitas/Auto-GPT/pull/4756
