# [C] CVE-2025-56005

## Summary
Severity: Critical
Advisory: CVE-2025-56005
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-20
Source: https://osv.dev/vulnerability/CVE-2025-56005
Type: osv

## Details
An undocumented and unsafe feature in the PLY (Python Lex-Yacc) library 3.11 allows Remote Code Execution (RCE) via the `picklefile` parameter in the `yacc()` function. This parameter accepts a `.pkl` file that is deserialized with `pickle.load()` without validation. Because `pickle` allows execution of embedded code via `__reduce__()`, an attacker can achieve code execution by passing a malicious pickle file. The parameter is not mentioned in official documentation or the GitHub repository, yet it is active in the PyPI version. This introduces a stealthy backdoor and persistence risk. NOTE: A third-party states that this vulnerability should be rejected because the proof of concept does not demonstrate arbitrary code execution and fails to complete successfully.

## References
- http://www.openwall.com/lists/oss-security/2026/01/23/4
- http://www.openwall.com/lists/oss-security/2026/01/23/5
- http://www.openwall.com/lists/oss-security/2026/01/28/5
- http://www.openwall.com/lists/oss-security/2026/01/29/1
- http://www.openwall.com/lists/oss-security/2026/01/29/2
- http://www.openwall.com/lists/oss-security/2026/01/30/1
- https://security.access.redhat.com/data/csaf/v2/vex/2025/cve-2025-56005.json
- https://access.redhat.com/security/cve/CVE-2025-56005
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/56xxx/CVE-2025-56005.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-56005
- https://bugzilla.redhat.com/show_bug.cgi?id=2431308
- https://github.com/tom025/ply_exploit_rejection/issues/1
- https://github.com/bohmiiidd/Undocumented-RCE-in-PLY
- https://github.com/bohmiiidd/Undocumument_RCE_PLY-yacc-CVE-2025-56005
- https://github.com/tom025/ply_exploit_rejection
