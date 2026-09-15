# [H] CVE-2019-19604

## Summary
Severity: High
Advisory: CVE-2019-19604
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-12-11
Source: https://osv.dev/vulnerability/CVE-2019-19604
Type: osv

## Details
Arbitrary command execution is possible in Git before 2.20.2, 2.21.x before 2.21.1, 2.22.x before 2.22.2, 2.23.x before 2.23.1, and 2.24.x before 2.24.1 because a "git submodule update" operation can run commands found in the .gitmodules file of a malicious repository.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HCYSSCA5ZTEP46SB4XRPSQGFV2L3NKMZ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/N6UGTEOXWIYSM5KDZL74QD2GK6YQNQCP/
- https://public-inbox.org/git/xmqqr21cqcn9.fsf%40gitster-ct.c.googlers.com/
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00056.html
- http://lists.opensuse.org/opensuse-security-announce/2020-05/msg00003.html
- http://www.openwall.com/lists/oss-security/2019/12/13/1
- https://raw.githubusercontent.com/git/git/master/Documentation/RelNotes/2.24.1.txt
- https://security.gentoo.org/glsa/202003-30
- https://www.debian.org/security/2019/dsa-4581
- https://gitlab.com/gitlab-com/gl-security/disclosures/blob/master/003_git_submodule/advisory.md
