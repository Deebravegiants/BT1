# [M] CVE-2017-7764

## Summary
Severity: Medium
Advisory: CVE-2017-7764
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2018-06-11
Source: https://osv.dev/vulnerability/CVE-2017-7764
Type: osv

## Details
Characters from the "Canadian Syllabics" unicode block can be mixed with characters from other unicode blocks in the addressbar instead of being rendered as their raw "punycode" form, allowing for domain name spoofing attacks through character confusion. The current Unicode standard allows characters from "Aspirational Use Scripts" such as Canadian Syllabics to be mixed with Latin characters in the "moderately restrictive" IDN profile. We have changed Firefox behavior to match the upcoming Unicode version 10.0 which removes this category and treats them as "Limited Use Scripts.". This vulnerability affects Firefox < 54, Firefox ESR < 52.2, and Thunderbird < 52.2.

## References
- https://access.redhat.com/errata/RHSA-2017:1440
- https://www.debian.org/security/2017/dsa-3881
- https://www.mozilla.org/security/advisories/mfsa2017-16/
- https://access.redhat.com/errata/RHSA-2017:1561
- https://www.debian.org/security/2017/dsa-3918
- https://www.mozilla.org/security/advisories/mfsa2017-15/
- https://www.mozilla.org/security/advisories/mfsa2017-17/
- http://www.securityfocus.com/bid/99057
- http://www.securitytracker.com/id/1038689
- http://www.unicode.org/reports/tr31/tr31-26.html#Aspirational_Use_Scripts
- https://bugzilla.mozilla.org/show_bug.cgi?id=1364283
