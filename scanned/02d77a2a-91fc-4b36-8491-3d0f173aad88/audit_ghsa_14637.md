# [H] Next.js authorization bypass vulnerability

## Summary
Severity: High
Advisory: GHSA-7gfc-8cq8-jh5f
CVE: CVE-2024-51479
CWE: CWE-285, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-12-17
Source: https://github.com/advisories/GHSA-7gfc-8cq8-jh5f
Type: github-advisory

## Affected
- npm: `next` — affected >=9.5.5 <14.2.15

## Details
### Impact
If a Next.js application is performing authorization in middleware based on pathname, it was possible for this authorization to be bypassed.

### Patches
This issue was patched in Next.js `14.2.15` and later.

If your Next.js application is hosted on Vercel, this vulnerability has been automatically mitigated, regardless of Next.js version.

### Workarounds
There are no official workarounds for this vulnerability.

#### Credits
We'd like to thank [tyage](http://github.com/tyage) (GMO CyberSecurity by IERAE) for responsible disclosure of this issue.

## References
- https://github.com/vercel/next.js/security/advisories/GHSA-7gfc-8cq8-jh5f
- https://nvd.nist.gov/vuln/detail/CVE-2024-51479
- https://github.com/vercel/next.js/commit/1c8234eb20bc8afd396b89999a00f06b61d72d7b
- https://github.com/vercel/next.js
- https://github.com/vercel/next.js/releases/tag/v14.2.15
