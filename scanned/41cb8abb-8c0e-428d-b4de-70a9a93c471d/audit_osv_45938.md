# [M] Libgcrypt before 1.12.2 mishandles Dilithium signing

## Summary
Severity: Medium
Advisory: JLSEC-2026-497
Ecosystem: Julia
CVSS: 4.0 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:L)
Published: 2026-05-14
Source: https://osv.dev/vulnerability/JLSEC-2026-497
Type: osv

## Affected
- Julia: `Libgcrypt_jll` — affected >=1.12.0+0 <1.12.2+0

## Details
Libgcrypt before 1.12.2 mishandles Dilithium signing. Writes to a static array lack a bounds check but do not use attacker-controlled data.

## References
- https://dev.gnupg.org/T8208
- https://github.com/advisories/GHSA-78pv-qq8x-94px
- https://lists.gnupg.org/pipermail/gnupg-announce/2026q2/000503.html
- https://nvd.nist.gov/vuln/detail/CVE-2026-41990
- https://www.openwall.com/lists/oss-security/2026/04/21/1
