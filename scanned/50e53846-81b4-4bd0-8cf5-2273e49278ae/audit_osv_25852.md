# [H] CVE-2023-46045

## Summary
Severity: High
Advisory: CVE-2023-46045
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-02-02
Source: https://osv.dev/vulnerability/CVE-2023-46045
Type: osv

## Details
Graphviz 2.36.0 through 9.x before 10.0.1 has an out-of-bounds read via a crafted config6a file. NOTE: exploitability may be uncommon because this file is typically owned by root.

## References
- http://packetstormsecurity.com/files/176816/graphviz-2.43.0-Buffer-Overflow-Code-Execution.html
- http://seclists.org/fulldisclosure/2024/Jan/62
- http://seclists.org/fulldisclosure/2024/Jan/73
- https://seclists.org/fulldisclosure/2024/Feb/24
- https://seclists.org/fulldisclosure/2024/Jan/73
- https://www.openwall.com/lists/oss-security/2024/02/01/2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/46xxx/CVE-2023-46045.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-46045
- https://gitlab.com/graphviz/graphviz/-/issues/2441
- http://seclists.org/fulldisclosure/2024/Feb/24
