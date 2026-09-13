# [H] CVE-2026-13442

## Summary
Severity: High
Advisory: CVE-2026-13442
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N)
Published: 2026-07-28
Source: https://osv.dev/vulnerability/CVE-2026-13442
Type: osv

## Details
IBM Langflow OSS 1.0.0 through 1.10.1 can allow an attacker to reuse another user's FAISS namespace to access owner-only vector content and influence later query results. This causes cross-user information disclosure and limited integrity impact through persistent poisoning of returned results.

## References
- https://www.ibm.com/support/pages/node/7279988
