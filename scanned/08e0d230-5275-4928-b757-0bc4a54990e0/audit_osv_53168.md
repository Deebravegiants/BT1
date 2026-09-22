# [M] CVE-2022-31744

## Summary
Severity: Medium
Advisory: CVE-2022-31744
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-31744
Type: osv

## Details
An attacker could have injected CSS into stylesheets accessible via internal URIs, such as resource:, and in doing so bypass a page's Content Security Policy. This vulnerability affects Firefox ESR < 91.11, Thunderbird < 102, Thunderbird < 91.11, and Firefox < 101.

## References
- https://www.mozilla.org/security/advisories/mfsa2022-20/
- https://www.mozilla.org/security/advisories/mfsa2022-25/
- https://www.mozilla.org/security/advisories/mfsa2022-26/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1757604
