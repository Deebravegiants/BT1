# [H] CVE-2023-0767

## Summary
Severity: High
Advisory: CVE-2023-0767
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-06-02
Source: https://osv.dev/vulnerability/CVE-2023-0767
Type: osv

## Details
An attacker could construct a PKCS 12 cert bundle in such a way that could allow for arbitrary memory writes via PKCS 12 Safe Bag attributes being mishandled. This vulnerability affects Firefox < 110, Thunderbird < 102.8, and Firefox ESR < 102.8.

## References
- https://alas.aws.amazon.com/AL2/ALAS-2023-1992.html
- https://www.mozilla.org/security/advisories/mfsa2023-05/
- https://www.mozilla.org/security/advisories/mfsa2023-06/
- https://www.mozilla.org/security/advisories/mfsa2023-07/
- https://security.netapp.com/advisory/ntap-20230324-0008/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1804640
