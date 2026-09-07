# [M] Open Redirect in Next.js

## Summary
Severity: Medium
Advisory: GHSA-vxf5-wxwp-m7g9
CVE: CVE-2021-37699
CWE: CWE-601
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2021-08-12
Source: https://github.com/advisories/GHSA-vxf5-wxwp-m7g9
Type: github-advisory

## Affected
- npm: `next` — affected >=0.9.9 <11.1.0

## Details
Next.js is an open source website development framework to be used with the React library. In affected versions specially encoded paths could be used when `pages/_error.js` was statically generated, allowing an open redirect to occur to an external site. In general, this redirect does not directly harm users although it can allow for phishing attacks by redirecting to an attacker's domain from a trusted domain.

### Impact

- **Affected:** Users of Next.js between `10.0.5` and `10.2.0`
- **Affected:** Users of Next.js between `11.0.0` and `11.0.1` using `pages/_error.js` without `getInitialProps`
- **Affected:** Users of Next.js between `11.0.0` and `11.0.1` using `pages/_error.js` and `next export`
- **Not affected**: Deployments on Vercel ([vercel.com](https://vercel.com)) are not affected
- **Not affected:** Deployments **with** `pages/404.js`
- Note that versions prior to 0.9.9 package `next` npm package hosted a different utility (0.4.1 being the latest version of that codebase), and this advisory does not apply to those versions.

We recommend upgrading to the latest version of Next.js to improve the overall security of your application.

### Patches

https://github.com/vercel/next.js/releases/tag/v11.1.0

## References
- https://github.com/vercel/next.js/security/advisories/GHSA-vxf5-wxwp-m7g9
- https://nvd.nist.gov/vuln/detail/CVE-2021-37699
- https://github.com/vercel/next.js
- https://github.com/vercel/next.js/releases/tag/v11.1.0
