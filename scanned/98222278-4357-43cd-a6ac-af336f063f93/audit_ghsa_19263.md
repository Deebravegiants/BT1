# [H] LLama-Index CLI OS command injection vulnerability

## Summary
Severity: High
Advisory: GHSA-g99h-56mw-8263
CVE: CVE-2025-1753
CWE: CWE-78
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-05-28
Source: https://github.com/advisories/GHSA-g99h-56mw-8263
Type: github-advisory

## Affected
- PyPI: `llama-index-cli` — affected >=0 <0.4.1

## Details
LLama-Index CLI prior to v0.4.1, corresponding to LLama-Index prior to v0.12.21, contains an OS command injection vulnerability. The vulnerability arises from the improper handling of the `--files` argument, which is directly passed into `os.system`. An attacker who controls the content of this argument can inject and execute arbitrary shell commands. This vulnerability can be exploited locally if the attacker has control over the CLI arguments, and remotely if a web application calls the LLama-Index CLI with a user-controlled filename. This issue can lead to arbitrary code execution on the affected system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-1753
- https://github.com/run-llama/llama_index/commit/b57e76738c53ca82d88658b82f2d82d1c7839c7d
- https://github.com/run-llama/llama_index
- https://huntr.com/bounties/19e1c67e-1d77-451d-b10b-acbe99900b22
