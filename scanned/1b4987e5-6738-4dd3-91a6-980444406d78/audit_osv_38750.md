# [M] CVE-2026-41990

## Summary
Severity: Medium
Advisory: CVE-2026-41990
CVSS: 4.0 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:L)
Published: 2026-04-23
Source: https://osv.dev/vulnerability/CVE-2026-41990
Type: osv

## Details
Libgcrypt before 1.12.2 mishandles Dilithium signing. Writes to a static array lack a bounds check but do not use attacker-controlled data.

## References
- https://dev.gnupg.org/T8208
- https://lists.gnupg.org/pipermail/gnupg-announce/2026q2/000503.html
- https://www.openwall.com/lists/oss-security/2026/04/21/1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41990.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-41990
