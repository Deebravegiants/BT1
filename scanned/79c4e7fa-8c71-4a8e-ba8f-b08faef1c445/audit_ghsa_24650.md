# [C] Dulwich Arbitrary code execution via commit with directory path starting with .git

## Summary
Severity: Critical
Advisory: GHSA-4j5j-58j7-6c3w
CVE: CVE-2014-9706
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-4j5j-58j7-6c3w
Type: github-advisory

## Affected
- PyPI: `dulwich` — affected >=0 <0.9.10

## Details
The `build_index_from_tree` function in index.py in Dulwich versions 0.9.9 and below allows remote attackers to execute arbitrary code via a commit with a directory path starting with `.git/`, which is not properly handled when checking out a working tree.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-9706
- https://github.com/jelmer/dulwich/commit/091638be3c89f46f42c3b1d57dc1504af5729176
- https://git.samba.org/?p=jelmer/dulwich.git;a=commitdiff;h=091638be3c89f46f42c3b1d57dc1504af5729176
- https://github.com/jelmer/dulwich
- https://github.com/pypa/advisory-database/tree/main/vulns/dulwich/PYSEC-2015-34.yaml
- https://lists.launchpad.net/dulwich-users/msg00827.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-April/154523.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-April/154551.html
- http://www.debian.org/security/2015/dsa-3206
- http://www.openwall.com/lists/oss-security/2015/03/21/1
- http://www.openwall.com/lists/oss-security/2015/03/22/26
