# [M] In GnuPG before 2.5.17, a long signature packet length causes `parse_signature` to return success...

## Summary
Severity: Medium
Advisory: JLSEC-2026-566
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/JLSEC-2026-566
Type: osv

## Affected
- Julia: `GnuPG_jll` — affected >=2.5.16+0 <2.5.17+0

## Details
In GnuPG before 2.5.17, a long signature packet length causes `parse_signature` to return success with sig->data[] set to a NULL value, leading to a denial of service (application crash).

## References
- https://dev.gnupg.org/T8049
- https://github.com/advisories/GHSA-7246-cvp4-g68w
- https://nvd.nist.gov/vuln/detail/CVE-2026-24883
- https://www.openwall.com/lists/oss-security/2026/01/27/8
