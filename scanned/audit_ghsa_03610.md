# [H] Arbitrary File Write in npm

## Summary
Severity: High
Advisory: GHSA-m6cx-g6qm-p2cx
CVE: CVE-2019-16775
CWE: CWE-59, CWE-61
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2019-12-13
Source: https://github.com/advisories/GHSA-m6cx-g6qm-p2cx
Type: github-advisory

## Affected
- npm: `npm` — affected >=0 <6.13.3

## Details
Versions of the npm CLI prior to 6.13.3 are vulnerable to an Arbitrary File Write. It fails to prevent access to folders outside of the intended node_modules folder through the bin field. A properly constructed entry in the package.json bin field would allow a package publisher to create files on a user's system when the package is installed. It is only possible to affect files that the user running `npm install` has access to and it is not possible to over write files that already exist on disk.

This behavior is still possible through install scripts. This vulnerability bypasses a user using the --ignore-scripts install option.


## Recommendation

Upgrade to version 6.13.3 or later.

## References
- https://github.com/npm/cli/security/advisories/GHSA-m6cx-g6qm-p2cx
- https://nvd.nist.gov/vuln/detail/CVE-2019-16775
- https://access.redhat.com/errata/RHEA-2020:0330
- https://access.redhat.com/errata/RHSA-2020:0573
- https://access.redhat.com/errata/RHSA-2020:0579
- https://access.redhat.com/errata/RHSA-2020:0597
- https://access.redhat.com/errata/RHSA-2020:0602
- https://blog.npmjs.org/post/189618601100/binary-planting-with-the-npm-cli
- https://github.com/advisories/GHSA-m6cx-g6qm-p2cx
- https://github.com/npm/cli
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/Z36UKPO5F3PQ3Q2POMF5LEKXWAH5RUFP
- https://www.npmjs.com/advisories/1434
- https://www.oracle.com/security-alerts/cpujan2020.html
- https://www.oracle.com/security-alerts/cpuoct2021.html
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00027.html
