# [M] Open Redirect in Next.js versions

## Summary
Severity: Medium
Advisory: GHSA-x56p-c8cg-q435
CVE: CVE-2020-15242
CWE: CWE-601
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2020-10-08
Source: https://github.com/advisories/GHSA-x56p-c8cg-q435
Type: github-advisory

## Affected
- npm: `next` — affected >=9.5.0 <9.5.4

## Details
### Impact

- **Affected**: Users of Next.js between 9.5.0 and 9.5.3 
- **Not affected**: Deployments on Vercel ([https://vercel.com](https://vercel.com)) are not affected
- **Not affected**: Deployments using `next export`

We recommend everyone to upgrade regardless of whether you can reproduce the issue or not.

### Patches

https://github.com/vercel/next.js/releases/tag/v9.5.4

### References

https://github.com/vercel/next.js/releases/tag/v9.5.4

## References
- https://github.com/vercel/next.js/security/advisories/GHSA-x56p-c8cg-q435
- https://nvd.nist.gov/vuln/detail/CVE-2020-15242
- https://github.com/vercel/next.js
- https://github.com/zeit/next.js/releases/tag/v9.5.4
