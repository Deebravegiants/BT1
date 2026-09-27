# [M] CVE-2022-45410

## Summary
Severity: Medium
Advisory: CVE-2022-45410
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-45410
Type: osv

## Details
When a ServiceWorker intercepted a request with <code>FetchEvent</code>, the origin of the request was lost after the ServiceWorker took ownership of it. This had the effect of negating SameSite cookie protections. This was addressed in the spec and then in browsers. This vulnerability affects Firefox ESR < 102.5, Thunderbird < 102.5, and Firefox < 107.

## References
- https://www.mozilla.org/security/advisories/mfsa2022-47/
- https://www.mozilla.org/security/advisories/mfsa2022-48/
- https://www.mozilla.org/security/advisories/mfsa2022-49/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1658869
