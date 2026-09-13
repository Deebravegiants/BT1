# [H] CVE-2020-9274

## Summary
Severity: High
Advisory: CVE-2020-9274
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-02-26
Source: https://osv.dev/vulnerability/CVE-2020-9274
Type: osv

## Details
An issue was discovered in Pure-FTPd 1.0.49. An uninitialized pointer vulnerability has been detected in the diraliases linked list. When the *lookup_alias(const char alias) or print_aliases(void) function is called, they fail to correctly detect the end of the linked list and try to access a non-existent list member. This is related to init_aliases in diraliases.c.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/22P44PECZWNDP7CMBL7NRBMNFS73C5Z2/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/B5NSUDWXZVWUCL6R2PTX3KBB42Z62CA5/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/U5DBVHJCXWRSJPNJQCJQCKZF6ZDPZCKA/
- https://lists.debian.org/debian-lts-announce/2020/02/msg00029.html
- https://security.gentoo.org/glsa/202003-54
- https://usn.ubuntu.com/4515-1/
- https://www.pureftpd.org/project/pure-ftpd/news/
- https://github.com/jedisct1/pure-ftpd/commit/8d0d42542e2cb7a56d645fbe4d0ef436e38bcefa
