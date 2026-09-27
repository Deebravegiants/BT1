# [M] Directory Traversal in Next.js

## Summary
Severity: Medium
Advisory: GHSA-fq77-7p7r-83rj
CVE: CVE-2020-5284
CWE: CWE-23
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2020-03-30
Source: https://github.com/advisories/GHSA-fq77-7p7r-83rj
Type: github-advisory

## Affected
- npm: `next` — affected >=0.9.9 <9.3.2

## Details
### Impact

- **Not affected**: Deployments on ZEIT Now v2 ([https://zeit.co](https://zeit.co/)) are not affected
- **Not affected**: Deployments using the `serverless` target
- **Not affected**: Deployments using `next export`
- **Affected**: Users of Next.js below 9.3.2

We recommend everyone to upgrade regardless of whether you can reproduce the issue or not.

### Patches

https://github.com/zeit/next.js/releases/tag/v9.3.2

### References

https://github.com/zeit/next.js/releases/tag/v9.3.2

## References
- https://github.com/zeit/next.js/security/advisories/GHSA-fq77-7p7r-83rj
- https://nvd.nist.gov/vuln/detail/CVE-2020-5284
- https://github.com/zeit/next.js/releases/tag/v9.3.2
- https://www.npmjs.com/advisories/1503
