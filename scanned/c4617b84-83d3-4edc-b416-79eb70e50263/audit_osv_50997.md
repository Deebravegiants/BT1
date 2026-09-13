# [M] CVE-2020-6829

## Summary
Severity: Medium
Advisory: CVE-2020-6829
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2020-10-28
Source: https://osv.dev/vulnerability/CVE-2020-6829
Type: osv

## Details
When performing EC scalar point multiplication, the wNAF point multiplication algorithm was used; which leaked partial information about the nonce used during signature generation. Given an electro-magnetic trace of a few signature generations, the private key could have been computed. This vulnerability affects Firefox < 80 and Firefox for Android < 80.

## References
- https://lists.debian.org/debian-lts-announce/2023/02/msg00021.html
- https://www.mozilla.org/security/advisories/mfsa2020-36/
- https://www.mozilla.org/security/advisories/mfsa2020-39/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1631583
