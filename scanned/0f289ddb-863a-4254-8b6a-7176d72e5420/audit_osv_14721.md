# [M] CVE-2019-11038

## Summary
Severity: Medium
Advisory: CVE-2019-11038
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2019-06-19
Source: https://osv.dev/vulnerability/CVE-2019-11038
Type: osv

## Details
When using the gdImageCreateFromXbm() function in the GD Graphics Library (aka LibGD) 2.2.5, as used in the PHP GD extension in PHP versions 7.1.x below 7.1.30, 7.2.x below 7.2.19 and 7.3.x below 7.3.6, it is possible to supply data that will cause the function to use the value of uninitialized variable. This may lead to disclosing contents of the stack that has been left there by previous code.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3CZ2QADQTKRHTGB2AHD7J4QQNDLBEMM6/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PKSSWFR2WPMUOIB5EN5ZM252NNEPYUTG/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WAZBVK6XNYEIN7RDQXESSD63QHXPLKWL/
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00020.html
- https://access.redhat.com/errata/RHSA-2019:2519
- https://access.redhat.com/errata/RHSA-2019:3299
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=929821
- https://bugs.php.net/bug.php?id=77973
- https://lists.debian.org/debian-lts-announce/2019/06/msg00003.html
- https://seclists.org/bugtraq/2019/Sep/38
- https://usn.ubuntu.com/4316-1/
- https://usn.ubuntu.com/4316-2/
- https://www.debian.org/security/2019/dsa-4529
- https://bugzilla.redhat.com/show_bug.cgi?id=1724149
- https://bugzilla.redhat.com/show_bug.cgi?id=1724432
- https://bugzilla.suse.com/show_bug.cgi?id=1140118
- https://bugzilla.suse.com/show_bug.cgi?id=1140120
- https://github.com/libgd/libgd/issues/501
