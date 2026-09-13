# [M] Unexpected server crash in Next.js version 12.2.3

## Summary
Severity: Medium
Advisory: CVE-2022-36046
Aliases: GHSA-wff4-fpwg-qqv3, PYSEC-2022-43188
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-08-31
Source: https://osv.dev/vulnerability/CVE-2022-36046
Type: osv

## Details
Next.js is a React framework that can provide building blocks to create web applications. All of the following must be true to be affected by this CVE: Next.js version 12.2.3, Node.js version above v15.0.0 being used with strict `unhandledRejection` exiting AND using next start or a [custom server](https://nextjs.org/docs/advanced-features/custom-server). Deployments on Vercel ([vercel.com](https://vercel.com/)) are not affected along with similar environments where `next-server` isn't being shared across requests.

## References
- https://github.com/vercel/next.js/releases/tag/v12.2.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/36xxx/CVE-2022-36046.json
- https://github.com/vercel/next.js/security/advisories/GHSA-wff4-fpwg-qqv3
- https://nvd.nist.gov/vuln/detail/CVE-2022-36046
