# [M] Denial of Service Vulnerability in next.js

## Summary
Severity: Medium
Advisory: GHSA-wr66-vrwm-5g5x
CVE: CVE-2022-21721
CWE: CWE-20, CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-01-28
Source: https://github.com/advisories/GHSA-wr66-vrwm-5g5x
Type: github-advisory

## Affected
- npm: `next` — affected >=12.0.0 <12.0.9

## Details
### Impact

Vulnerable code could allow a bad actor to trigger a denial of service attack for anyone running a Next.js app at version >= 12.0.0, and using i18n functionality.

- **Affected:** All of the following must be true to be affected by this CVE
  - Next.js versions above v12.0.0
  - Using next start or a custom server
  - Using the built-in i18n support
- **Not affected:**
  - Deployments on Vercel (vercel.com) are not affected along with similar environments where invalid requests are filtered before reaching Next.js.

### Patches

A patch has been released, `next@12.0.9`, that mitigates this issue. We recommend all affected users upgrade as soon as possible.

### Workarounds

We recommend upgrading whether you can reproduce or not although you can ensure `/${locale}/_next/` is blocked from reaching the Next.js instance until you upgrade.

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [next](https://github.com/vercel/next.js)
* Email us at [security@vercel.com](mailto:security@vercel.com)

## References
- https://github.com/vercel/next.js/security/advisories/GHSA-wr66-vrwm-5g5x
- https://nvd.nist.gov/vuln/detail/CVE-2022-21721
- https://github.com/vercel/next.js/pull/33503
- https://github.com/vercel/next.js
- https://github.com/vercel/next.js/releases/tag/v12.0.9
