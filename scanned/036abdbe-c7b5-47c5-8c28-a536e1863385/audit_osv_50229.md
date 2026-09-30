# [H] CVE-2019-9813

## Summary
Severity: High
Advisory: CVE-2019-9813
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-04-26
Source: https://osv.dev/vulnerability/CVE-2019-9813
Type: osv

## Details
Incorrect handling of __proto__ mutations may lead to type confusion in IonMonkey JIT code and can be leveraged for arbitrary memory read and write. This vulnerability affects Firefox < 66.0.1, Firefox ESR < 60.6.1, and Thunderbird < 60.6.1.

## References
- https://www.mozilla.org/security/advisories/mfsa2019-12/
- https://access.redhat.com/errata/RHSA-2019:0966
- https://access.redhat.com/errata/RHSA-2019:1144
- https://www.mozilla.org/security/advisories/mfsa2019-09/
- https://www.mozilla.org/security/advisories/mfsa2019-10/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1538006
