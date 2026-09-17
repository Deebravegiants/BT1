# [M] CVE-2020-12401

## Summary
Severity: Medium
Advisory: CVE-2020-12401
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-10-08
Source: https://osv.dev/vulnerability/CVE-2020-12401
Type: osv

## Details
During ECDSA signature generation, padding applied in the nonce designed to ensure constant-time scalar multiplication was removed, resulting in variable-time execution dependent on secret data. This vulnerability affects Firefox < 80 and Firefox for Android < 80.

## References
- https://lists.debian.org/debian-lts-announce/2023/02/msg00021.html
- https://www.mozilla.org/security/advisories/mfsa2020-36/
- https://www.mozilla.org/security/advisories/mfsa2020-39/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1631573
