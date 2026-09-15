# [M] CVE-2016-2167

## Summary
Severity: Medium
Advisory: CVE-2016-2167
CVSS: 6.8 (CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2016-05-05
Source: https://osv.dev/vulnerability/CVE-2016-2167
Type: osv

## Details
The canonicalize_username function in svnserve/cyrus_auth.c in Apache Subversion before 1.8.16 and 1.9.x before 1.9.4, when Cyrus SASL authentication is used, allows remote attackers to authenticate and bypass intended access restrictions via a realm string that is a prefix of an expected repository realm string.

## References
- http://lists.fedoraproject.org/pipermail/package-announce/2016-May/184545.html
- http://lists.opensuse.org/opensuse-updates/2016-05/msg00043.html
- http://lists.opensuse.org/opensuse-updates/2016-05/msg00044.html
- http://mail-archives.apache.org/mod_mbox/subversion-announce/201604.mbox/%3CCAP_GPNgJet+7_MAhomFVOXPgLtewcUw9w=k9zdPCkq5tvPxVMA%40mail.gmail.com%3E
- http://mail-archives.apache.org/mod_mbox/subversion-announce/201604.mbox/%3CCAP_GPNgfn1iKueW51EpmXzXi_URNfGNofZSgOyW1_jnSeNm5DQ%40mail.gmail.com%3E
- http://www.securityfocus.com/bid/89417
- http://www.securitytracker.com/id/1035706
- http://www.slackware.com/security/viewer.php?l=slackware-security&y=2016&m=slackware-security.417496
- https://www.oracle.com/security-alerts/cpuoct2020.html
- http://subversion.apache.org/security/CVE-2016-2167-advisory.txt
- http://www.debian.org/security/2016/dsa-3561
- https://security.gentoo.org/glsa/201610-05
