# [H] CVE-2025-24528

## Summary
Severity: High
Advisory: CVE-2025-24528
CVSS: 7.1 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:N/I:L/A:H)
Published: 2026-01-16
Source: https://osv.dev/vulnerability/CVE-2025-24528
Type: osv

## Details
In MIT Kerberos 5 (aka krb5) before 1.22 (with incremental propagation), there is an integer overflow for a large update size to resize() in kdb_log.c. An authenticated attacker can cause an out-of-bounds write and kadmind daemon crash.

## References
- https://github.com/krb5/krb5/compare/krb5-1.21.3-final...krb5-1.22-final
- https://lists.debian.org/debian-lts-announce/2025/02/msg00029.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/24xxx/CVE-2025-24528.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-24528
- https://github.com/krb5/krb5/commit/78ceba024b64d49612375be4a12d1c066b0bfbd0
