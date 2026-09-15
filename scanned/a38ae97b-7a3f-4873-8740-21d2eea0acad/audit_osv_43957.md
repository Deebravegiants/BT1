# [C] Agno PythonTools Path Traversal via joinpath file_name argument

## Summary
Severity: Critical
Advisory: CVE-2026-76832
CVSS: 9.0 (CVSS:4.0/AV:A/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-76832
Type: osv

## Details
Agno's PythonTools in libs/agno/agno/tools/python.py contains a path traversal vulnerability that allows attackers to read, write, or execute arbitrary files by supplying parent-directory traversal sequences in the file_name argument passed to read_file, save_to_file, or run_python_file tool actions. Attackers can inject traversal sequences such as '../../../../../../etc/passwd' through direct tool invocation or via prompt injection embedded in agent-processed content to escape the intended base_dir boundary and achieve arbitrary file read, arbitrary file write, or arbitrary Python code execution within the process user's authority.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/76xxx/CVE-2026-76832.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-76832
- https://www.vulncheck.com/advisories/agno-pythontools-path-traversal-via-joinpath-file-name-argument
- https://github.com/agno-agi/agno/commit/710d7e7f846f93b7a3eadfd3e77075428c39e803
- https://github.com/agno-agi/agno
