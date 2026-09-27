# [H] JLSEC-2026-1276

## Summary
Severity: High
Advisory: JLSEC-2026-1276
Ecosystem: Julia
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/JLSEC-2026-1276
Type: osv

## Affected
- Julia: `Graphviz_jll` — affected >=0 <15.1.0+0

## Details
Graphviz 2.36.0 through 9.x before 10.0.1 has an out-of-bounds read via a crafted config6a file. NOTE: exploitability may be uncommon because this file is typically owned by root.

## References
- http://packetstormsecurity.com/files/176816/graphviz-2.43.0-Buffer-Overflow-Code-Execution.html
- http://seclists.org/fulldisclosure/2024/Feb/24
- http://seclists.org/fulldisclosure/2024/Feb/24
- http://seclists.org/fulldisclosure/2024/Jan/62
- http://seclists.org/fulldisclosure/2024/Jan/73
- https://gitlab.com/graphviz/graphviz/-/issues/2441
- https://gitlab.com/graphviz/graphviz/-/issues/2441
- https://seclists.org/fulldisclosure/2024/Feb/24
- https://seclists.org/fulldisclosure/2024/Feb/24
- https://seclists.org/fulldisclosure/2024/Jan/73
- https://seclists.org/fulldisclosure/2024/Jan/73
- https://www.openwall.com/lists/oss-security/2024/02/01/2
- https://www.openwall.com/lists/oss-security/2024/02/01/2
