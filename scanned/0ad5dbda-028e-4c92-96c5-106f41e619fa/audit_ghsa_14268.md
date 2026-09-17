# [C] @nuxtlabs/github-module made Use of Hard-coded Credentials

## Summary
Severity: Critical
Advisory: GHSA-fp2w-g92g-fgq4
CVE: CVE-2023-2138
CWE: CWE-798
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-04-18
Source: https://github.com/advisories/GHSA-fp2w-g92g-fgq4
Type: github-advisory

## Affected
- npm: `@nuxtlabs/github-module` — affected >=0 <1.6.2

## Details
https://nuxt.com had a hardcoded GitHub token in the source code of the page. This token had access to multiple repositories under `nuxt`, `nuxtlabs` and `nuxt-themes` GitHub organizations. A patch in version 1.6.2 fixed the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-2138
- https://github.com/nuxtlabs/github-module/commit/5490c43f729eee60f07920bf88c0aabdc1398b6e
- https://github.com/nuxtlabs/github-module
- https://github.com/nuxtlabs/github-module/releases/tag/v1.6.2
- https://huntr.dev/bounties/65096ef9-eafc-49da-b49a-5b88c0203ca6
