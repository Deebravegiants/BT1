# [H] OpenChatBI has a Path Traversal Vulnerability in save_report Tool

## Summary
Severity: High
Advisory: GHSA-vmwq-8g8c-jm79
CVE: CVE-2026-28795
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-02
Source: https://github.com/advisories/GHSA-vmwq-8g8c-jm79
Type: github-advisory

## Affected
- PyPI: `openchatbi` — affected >=0 <0.2.2

## Details
### Impact
The `save_report` tool in `openchatbi/tool/save_report.py` suffers from a critical path traversal vulnerability due to insufficient input sanitization of the `file_format` parameter. 

The function only removes leading dots of `file_format` using `file_format.lstrip(".")` but allows path traversal sequences like `/../../` to pass through unchanged. When the filename is constructed via string concatenation in 

    f"{timestamp}_{clean_title}.{file_format}"

malicious path sequences are preserved, enabling attackers to write files outside the designated report directory. 

An attacker can manipulate the LLM to call the tool with a specific `file_format` to overwrite critical system files like `__init__.py`, potentially leading to remote code execution.


### Patches
- Affected versions:
<=0.2.1
- Patched versions:
0.2.2 (includes fix from PR #12: https://github.com/zhongyu09/openchatbi/pull/12)

### Workarounds
No

### References
- Issue #10: https://github.com/zhongyu09/openchatbi/issues/10
- PR #12: https://github.com/zhongyu09/openchatbi/pull/12

## References
- https://github.com/zhongyu09/openchatbi/security/advisories/GHSA-vmwq-8g8c-jm79
- https://nvd.nist.gov/vuln/detail/CVE-2026-28795
- https://github.com/zhongyu09/openchatbi/issues/10
- https://github.com/zhongyu09/openchatbi/pull/12
- https://github.com/zhongyu09/openchatbi/commit/372a7e861da5159c3106d64d6f6edf8284db8c75
- https://github.com/zhongyu09/openchatbi
