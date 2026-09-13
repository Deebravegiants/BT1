# [H] loader-utils is vulnerable to Regular Expression Denial of Service (ReDoS)

## Summary
Severity: High
Advisory: GHSA-hhq3-ff78-jv3g
CVE: CVE-2022-37599
CWE: CWE-1333, CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-10-12
Source: https://github.com/advisories/GHSA-hhq3-ff78-jv3g
Type: github-advisory

## Affected
- npm: `loader-utils` — affected >=1.0.0 <1.4.2
- npm: `loader-utils` — affected >=2.0.0 <2.0.4
- npm: `loader-utils` — affected >=3.0.0 <3.2.1

## Details
A regular expression denial of service (ReDoS) flaw was found in Function interpolateName in interpolateName.js in webpack loader-utils via the resourcePath variable in interpolateName.js. A badly or maliciously formed string could be used to send crafted requests that cause a system to crash or take a disproportional amount of time to process. This issue has been patched in versions 1.4.2, 2.0.4 and 3.2.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-37599
- https://github.com/webpack/loader-utils/issues/211
- https://github.com/webpack/loader-utils/issues/216
- https://github.com/webpack/loader-utils/commit/17cbf8fa8989c1cb45bdd2997aa524729475f1fa
- https://github.com/webpack/loader-utils/commit/ac09944dfacd7c4497ef692894b09e63e09a5eeb
- https://github.com/webpack/loader-utils/commit/d2d752d59629daee38f34b24307221349c490eb1
- https://github.com/webpack/loader-utils
- https://github.com/webpack/loader-utils/blob/d9f4e23cf411d8556f8bac2d3bf05a6e0103b568/lib/interpolateName.js#L38
- https://github.com/webpack/loader-utils/blob/d9f4e23cf411d8556f8bac2d3bf05a6e0103b568/lib/interpolateName.js#L83
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3HUE6ZR5SL73KHL7XUPAOEL6SB7HUDT2
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6PVVPNSAGSDS63HQ74PJ7MZ3MU5IYNVZ
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/6PVVPNSAGSDS63HQ74PJ7MZ3MU5IYNVZ
