# [C] Authorization Bypass in Next.js Middleware

## Summary
Severity: Critical
Advisory: GHSA-f82v-jwr5-mffw
CVE: CVE-2025-29927
CWE: CWE-285, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-03-21
Source: https://github.com/advisories/GHSA-f82v-jwr5-mffw
Type: github-advisory

## Affected
- npm: `next` — affected >=13.0.0 <13.5.9
- npm: `next` — affected >=14.0.0 <14.2.25
- npm: `next` — affected >=15.0.0 <15.2.3
- npm: `next` — affected >=12.0.0 <12.3.5

## Details
# Impact
It is possible to bypass authorization checks within a Next.js application, if the authorization check occurs in middleware.

# Patches
* For Next.js 15.x, this issue is fixed in `15.2.3`
* For Next.js 14.x, this issue is fixed in `14.2.25`
* For Next.js 13.x, this issue is fixed in 13.5.9
* For Next.js 12.x, this issue is fixed in 12.3.5
* For Next.js 11.x, consult the below workaround.

_Note: Next.js deployments hosted on Vercel are automatically protected against this vulnerability._

# Workaround
If patching to a safe version is infeasible, we recommend that you prevent external user requests which contain the `x-middleware-subrequest` header from reaching your Next.js application.

## Credits

- Allam Rachid (zhero;)
- Allam Yasser (inzo_)

## References
- https://github.com/vercel/next.js/security/advisories/GHSA-f82v-jwr5-mffw
- https://nvd.nist.gov/vuln/detail/CVE-2025-29927
- https://github.com/vercel/next.js/commit/52a078da3884efe6501613c7834a3d02a91676d2
- https://github.com/vercel/next.js/commit/5fd3ae8f8542677c6294f32d18022731eab6fe48
- https://github.com/vercel/next.js
- https://github.com/vercel/next.js/releases/tag/v12.3.5
- https://github.com/vercel/next.js/releases/tag/v13.5.9
- https://security.netapp.com/advisory/ntap-20250328-0002
- https://vercel.com/changelog/vercel-firewall-proactively-protects-against-vulnerability-with-middleware
- http://www.openwall.com/lists/oss-security/2025/03/23/3
- http://www.openwall.com/lists/oss-security/2025/03/23/4
