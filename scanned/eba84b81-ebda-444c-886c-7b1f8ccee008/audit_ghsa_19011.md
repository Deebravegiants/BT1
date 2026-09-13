# [M] Nuxt DevTools vulnerable to cross-site scripting (XSS)

## Summary
Severity: Medium
Advisory: GHSA-xmq3-q5pm-rp26
CVE: CVE-2025-52662
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:L/I:H/A:N (CVSS_V3)
Published: 2025-11-07
Source: https://github.com/advisories/GHSA-xmq3-q5pm-rp26
Type: github-advisory

## Affected
- npm: `@nuxt/devtools` — affected >=0 <2.6.4

## Details
A vulnerability in Nuxt DevTools has been fixed in version **2.6.4***. This issue may have allowed Nuxt auth token extraction via XSS under certain configurations. All users are encouraged to upgrade.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-52662
- https://github.com/nuxt/devtools/commit/7cadbbe9
- https://github.com/nuxt/devtools
- https://github.com/nuxt/devtools/releases/tag/v2.6.4
- https://vercel.com/changelog/cve-2025-52662-xss-on-nuxt-devtools
