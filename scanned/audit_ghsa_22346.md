# [C] Exposure of Sensitive Information in eventsource

## Summary
Severity: Critical
Advisory: GHSA-6h5x-7c5m-7cr7
CVE: CVE-2022-1650
CWE: CWE-200, CWE-212
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-6h5x-7c5m-7cr7
Type: github-advisory

## Affected
- npm: `eventsource` — affected >=0 <1.1.1
- npm: `eventsource` — affected >=2.0.0 <2.0.2

## Details
When fetching an url with a link to an external site (Redirect), the users Cookies & Autorisation headers are leaked to the third party application. According to the same-origin-policy, the header should be "sanitized."

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-1650
- https://github.com/EventSource/eventsource/pull/273#issuecomment-1127624508
- https://github.com/EventSource/eventsource/commit/f9f6416567bff62c1af2f4314be51d9870e94bc2
- https://github.com/eventsource/eventsource/commit/10ee0c4881a6ba2fe65ec18ed195ac35889583c4
- https://github.com/eventsource/eventsource
- https://huntr.dev/bounties/dc9e467f-be5d-4945-867d-1044d27e9b8e
- https://lists.debian.org/debian-lts-announce/2022/12/msg00021.html
