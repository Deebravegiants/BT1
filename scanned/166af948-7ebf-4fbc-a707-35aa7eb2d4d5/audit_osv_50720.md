# [M] CVE-2020-35111

## Summary
Severity: Medium
Advisory: CVE-2020-35111
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N)
Published: 2021-01-07
Source: https://osv.dev/vulnerability/CVE-2020-35111
Type: osv

## Details
When an extension with the proxy permission registered to receive <all_urls>, the proxy.onRequest callback was not triggered for view-source URLs. While web content cannot navigate to such URLs, a user opening View Source could have inadvertently leaked their IP address. This vulnerability affects Firefox < 84, Thunderbird < 78.6, and Firefox ESR < 78.6.

## References
- https://www.mozilla.org/security/advisories/mfsa2020-54/
- https://www.mozilla.org/security/advisories/mfsa2020-55/
- https://www.mozilla.org/security/advisories/mfsa2020-56/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1657916
