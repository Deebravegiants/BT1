# [H] Next.JS vulnerability can lead to DoS via cache poisoning 

## Summary
Severity: High
Advisory: GHSA-67rr-84xm-4c7r
CVE: CVE-2025-49826
CWE: CWE-444
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-07-03
Source: https://github.com/advisories/GHSA-67rr-84xm-4c7r
Type: github-advisory

## Affected
- npm: `next` — affected >=15.0.4-canary.51 <15.1.8

## Details
### Summary
A vulnerability affecting Next.js has been addressed. It impacted versions 15.0.4 through 15.1.8 and involved a cache poisoning bug leading to a Denial of Service (DoS) condition.

Under certain conditions, this issue may allow a HTTP 204 response to be cached for static pages, leading to the 204 response being served to all users attempting to access the page

More details: [CVE-2025-49826](https://vercel.com/changelog/cve-2025-49826)

## Credits
- Allam Rachid [zhero;](https://zhero-web-sec.github.io/research-and-things/)
- Allam Yasser (inzo)

## References
- https://github.com/vercel/next.js/security/advisories/GHSA-67rr-84xm-4c7r
- https://nvd.nist.gov/vuln/detail/CVE-2025-49826
- https://github.com/vercel/next.js/commit/16bfce64ef2157f2c1dfedcfdb7771bc63103fd2
- https://github.com/vercel/next.js/commit/a15b974ed707d63ad4da5b74c1441f5b7b120e93
- https://github.com/vercel/next.js
- https://github.com/vercel/next.js/releases/tag/v15.1.8
- https://vercel.com/changelog/cve-2025-49826
