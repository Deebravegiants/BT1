# [H] CVE-2018-20834

## Summary
Severity: High
Advisory: CVE-2018-20834
Aliases: GHSA-j44m-qm6p-hp7m
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2019-04-30
Source: https://osv.dev/vulnerability/CVE-2018-20834
Type: osv

## Details
A vulnerability was found in node-tar before version 4.4.2 (excluding version 2.2.2). An Arbitrary File Overwrite issue exists when extracting a tarball containing a hardlink to a file that already exists on the system, in conjunction with a later plain file with the same name as the hardlink. This plain file content replaces the existing file content. A patch has been applied to node-tar v2.2.2).

## References
- https://github.com/npm/node-tar/commits/v2.2.2
- https://access.redhat.com/errata/RHSA-2019:1821
- https://nvd.nist.gov/vuln/detail/CVE-2018-20834
- https://github.com/npm/node-tar/commit/7ecef07da6a9e72cc0c4d0c9c6a8e85b6b52395d
- https://github.com/npm/node-tar/commit/b0c58433c22f5e7fe8b1c76373f27e3f81dcd4c8
- https://github.com/npm/node-tar/compare/58a8d43...a5f7779
- https://hackerone.com/reports/344595
