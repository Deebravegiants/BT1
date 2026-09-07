# [H] npm Vulnerable to Global node_modules Binary Overwrite

## Summary
Severity: High
Advisory: GHSA-4328-8hgf-7wjr
CVE: CVE-2019-16777
CWE: CWE-22, CWE-269
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2019-12-13
Source: https://github.com/advisories/GHSA-4328-8hgf-7wjr
Type: github-advisory

## Affected
- npm: `npm` — affected >=0 <6.13.4

## Details
Versions of  the npm CLI prior to 6.13.4 are vulnerable to a Global node_modules Binary Overwrite. It fails to prevent existing globally-installed binaries to be overwritten by other package installations. 

For example, if a package was installed globally and created a `serve` binary, any subsequent installs of packages that also create a `serve` binary would overwrite the first binary. This will not overwrite system binaries but only binaries put into the global node_modules directory.

This behavior is still allowed in local installations and also through install scripts. This vulnerability bypasses a user using the --ignore-scripts install option.


## Recommendation

Upgrade to version 6.13.4 or later.

## References
- https://github.com/npm/cli/security/advisories/GHSA-4328-8hgf-7wjr
- https://nvd.nist.gov/vuln/detail/CVE-2019-16777
- https://access.redhat.com/errata/RHEA-2020:0330
- https://access.redhat.com/errata/RHSA-2020:0573
- https://access.redhat.com/errata/RHSA-2020:0579
- https://access.redhat.com/errata/RHSA-2020:0597
- https://access.redhat.com/errata/RHSA-2020:0602
- https://blog.npmjs.org/post/189618601100/binary-planting-with-the-npm-cli
- https://github.com/advisories/GHSA-4328-8hgf-7wjr
- https://github.com/npm/cli
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/Z36UKPO5F3PQ3Q2POMF5LEKXWAH5RUFP
- https://security.gentoo.org/glsa/202003-48
- https://www.npmjs.com/advisories/1437
- https://www.oracle.com/security-alerts/cpujan2020.html
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00027.html
