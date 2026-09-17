# [M] CVE-2020-26961

## Summary
Severity: Medium
Advisory: CVE-2020-26961
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2020-12-09
Source: https://osv.dev/vulnerability/CVE-2020-26961
Type: osv

## Details
When DNS over HTTPS is in use, it intentionally filters RFC1918 and related IP ranges from the responses as these do not make sense coming from a DoH resolver. However when an IPv4 address was mapped through IPv6, these addresses were erroneously let through, leading to a potential DNS Rebinding attack. This vulnerability affects Firefox < 83, Firefox ESR < 78.5, and Thunderbird < 78.5.

## References
- https://www.mozilla.org/security/advisories/mfsa2020-52/
- https://www.mozilla.org/security/advisories/mfsa2020-50/
- https://www.mozilla.org/security/advisories/mfsa2020-51/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1672528
