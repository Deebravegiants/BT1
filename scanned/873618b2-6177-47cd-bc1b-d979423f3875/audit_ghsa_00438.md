# [H] Link Following in ansible

## Summary
Severity: High
Advisory: GHSA-rh6x-qvg7-rrmj
CVE: CVE-2016-3096
CWE: CWE-59
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-10-10
Source: https://github.com/advisories/GHSA-rh6x-qvg7-rrmj
Type: github-advisory

## Affected
- PyPI: `ansible` — affected >=2.0.0.0 <2.0.2.0
- PyPI: `ansible` — affected >=0 <1.9.6.1

## Details
The `create_script` function in the `lxc_container` module in Ansible before 1.9.6-1 and 2.x before 2.0.2.0 allows local users to write to arbitrary files or gain privileges via a symlink attack on (1) `/opt/.lxc-attach-script`, (2) the archived container in the `archive_path` directory, or the (3) `lxc-attach-script.log` or (4) `lxc-attach-script.err` files in the temporary directory.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-3096
- https://github.com/ansible/ansible-modules-extras/pull/1941
- https://github.com/ansible/ansible-modules-extras/commit/7c3999a92a1cd856ff9bc8913a93ff1aee8bffc3
- https://bugzilla.redhat.com/show_bug.cgi?id=1322925
- https://github.com/advisories/GHSA-rh6x-qvg7-rrmj
- https://github.com/ansible/ansible
- https://github.com/ansible/ansible/blob/v1.9.6-1/CHANGELOG.md#196-dancing-in-the-street---tbd
- https://github.com/ansible/ansible/blob/v2.0.2.0-1/CHANGELOG.md#202-over-the-hills-and-far-away
- https://github.com/pypa/advisory-database/tree/main/vulns/ansible/PYSEC-2016-1.yaml
- https://groups.google.com/forum/#!topic/ansible-announce/E80HLZilTU0
- https://groups.google.com/forum/#!topic/ansible-announce/tqiZbcWxYig
- https://groups.google.com/forum/#%21topic/ansible-announce/E80HLZilTU0
- https://groups.google.com/forum/#%21topic/ansible-announce/tqiZbcWxYig
- https://security.gentoo.org/glsa/201607-14
- http://lists.fedoraproject.org/pipermail/package-announce/2016-April/183103.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-April/183132.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-April/183252.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-April/183274.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-May/184175.html
