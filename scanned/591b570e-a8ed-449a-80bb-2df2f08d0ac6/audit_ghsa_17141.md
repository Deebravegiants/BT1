# [C] pgAdmin 4 vulnerable to Unsafe Deserialization and Remote Code Execution by an Authenticated user

## Summary
Severity: Critical
Advisory: GHSA-rj98-crf4-g69w
CVE: CVE-2024-2044
CWE: CWE-22, CWE-31, CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-03-07
Source: https://github.com/advisories/GHSA-rj98-crf4-g69w
Type: github-advisory

## Affected
- PyPI: `pgAdmin4` — affected >=0 <8.4

## Details
pgAdmin prior to version 8.4 is affected by a path-traversal vulnerability while deserializing users’ sessions in the session handling code. If the server is running on Windows, an unauthenticated attacker can load and deserialize remote pickle objects and gain code execution. If the server is running on POSIX/Linux, an authenticated attacker can upload pickle objects, deserialize them and gain code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-2044
- https://github.com/pgadmin-org/pgadmin4/issues/7258
- https://github.com/pgadmin-org/pgadmin4/commit/4e49d752fba72953acceeb7f4aa2e6e32d25853d
- https://github.com/pgadmin-org/pgadmin4
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/LUYN2JXKKHFSVTASH344TBRGWDH64XQV
- https://www.shielder.com/advisories/pgadmin-path-traversal_leads_to_unsafe_deserialization_and_rce
