# [M] node-tar Vulnerable to Arbitrary File Overwrite and Symlink Poisoning via Insufficient Path Sanitization

## Summary
Severity: Medium
Advisory: CVE-2026-23745
Aliases: GHSA-8qq5-rm4j-mr97
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:H/VI:L/VA:N/SC:H/SI:L/SA:N)
Published: 2026-01-16
Source: https://osv.dev/vulnerability/CVE-2026-23745
Type: osv

## Details
node-tar is a Tar for Node.js. The node-tar library (<= 7.5.2) fails to sanitize the linkpath of Link (hardlink) and SymbolicLink entries when preservePaths is false (the default secure behavior). This allows malicious archives to bypass the extraction root restriction, leading to Arbitrary File Overwrite via hardlinks and Symlink Poisoning via absolute symlink targets. This vulnerability is fixed in 7.5.3.

## References
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-23745.json
- https://access.redhat.com/errata/RHSA-2026:18480
- https://access.redhat.com/errata/RHSA-2026:18868
- https://access.redhat.com/errata/RHSA-2026:19712
- https://access.redhat.com/errata/RHSA-2026:2144
- https://access.redhat.com/errata/RHSA-2026:2900
- https://access.redhat.com/errata/RHSA-2026:2926
- https://access.redhat.com/errata/RHSA-2026:3782
- https://access.redhat.com/errata/RHSA-2026:41928
- https://access.redhat.com/errata/RHSA-2026:6192
- https://access.redhat.com/security/cve/CVE-2026-23745
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23745.json
- https://github.com/isaacs/node-tar/security/advisories/GHSA-8qq5-rm4j-mr97
- https://nvd.nist.gov/vuln/detail/CVE-2026-23745
- https://bugzilla.redhat.com/show_bug.cgi?id=2430538
- https://github.com/isaacs/node-tar/commit/340eb285b6d986e91969a1170d7fe9b0face405e
