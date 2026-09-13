# [H] Denial of Service vulnerability in @podium/layout and @podium/proxy

## Summary
Severity: High
Advisory: GHSA-3hjg-vc7r-rcrw
CVE: CVE-2022-24822
CWE: CWE-248
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-04-07
Source: https://github.com/advisories/GHSA-3hjg-vc7r-rcrw
Type: github-advisory

## Affected
- npm: `@podium/layout` — affected >=0 <4.6.110
- npm: `@podium/proxy` — affected >=0 <4.2.74

## Details
### Impact
An attacker using the `Trailer` header as part of the request against proxy endpoints has the ability to take down the server.
All Podium layouts that include podlets with proxy endpoints are affected.

### Patches
`@podium/layout` which is the main way developers/users are vulnerable to this exploit, has been patched in version `4.6.110`. All earlier versions are vulnerable.
`@podium/proxy` which is the source of the vulnerability and is used by `@podium/layout` has been patched in version `4.2.74`. All earlier versions are vulnerable.

### Workarounds
It is not easily possible to work around this issue without upgrading. We recommend upgrading `@podium/layout` and/or `@podium/proxy` as soon as possible.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [podium-lib/issues](https://github.com/podium-lib/issues)

### Credits
The vulnerability was reported by [krynos](https://hackerone.com/krynos) from [Ercoli Consulting](https://www.ercoliconsulting.eu/) via FINN.no's private bug bounty program

## References
- https://github.com/podium-lib/proxy/security/advisories/GHSA-3hjg-vc7r-rcrw
- https://nvd.nist.gov/vuln/detail/CVE-2022-24822
- https://github.com/podium-lib/layout/commit/fe43e655432b0a5f07b6475f67babcc2588fb039
- https://github.com/podium-lib/proxy/commit/9698a40df081217ce142d4de71f929baaa339cdf
- https://github.com/podium-lib/layout/releases/tag/v4.6.110
- https://github.com/podium-lib/proxy/releases/tag/v4.2.74
