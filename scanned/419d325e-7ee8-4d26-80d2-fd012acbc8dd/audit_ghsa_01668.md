# [H] Yarn Improper link resolution before file access (Link Following)

## Summary
Severity: High
Advisory: GHSA-5xf4-f2fq-f69j
CVE: CVE-2019-10773
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-02-14
Source: https://github.com/advisories/GHSA-5xf4-f2fq-f69j
Type: github-advisory

## Affected
- npm: `yarn` — affected >=0 <1.22.0

## Details
In Yarn before 1.21.1, the package install functionality can be abused to generate arbitrary symlinks on the host filesystem by using specially crafted "bin" keys. Existing files could be overwritten depending on the current user permission set.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10773
- https://github.com/yarnpkg/yarn/issues/7761#issuecomment-565493023
- https://github.com/yarnpkg/yarn/pull/7755
- https://github.com/yarnpkg/yarn/commit/039bafd74b7b1a88a53a54f8fa6fa872615e90e7
- https://access.redhat.com/errata/RHSA-2020:0475
- https://blog.daniel-ruf.de/critical-design-flaw-npm-pnpm-yarn
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/3HIZW4NZVV5QY5WWGW2JRP3FHYKZ6ZJ5
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ITY5BC63CCC647DFNUQRQ5AJDKUKUNBI
- https://snyk.io/vuln/SNYK-JS-YARN-537806,
