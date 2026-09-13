# [M] CVE-2016-2168

## Summary
Severity: Medium
Advisory: CVE-2016-2168
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-05-05
Source: https://osv.dev/vulnerability/CVE-2016-2168
Type: osv

## Details
The req_check_access function in the mod_authz_svn module in the httpd server in Apache Subversion before 1.8.16 and 1.9.x before 1.9.4 allows remote authenticated users to cause a denial of service (NULL pointer dereference and crash) via a crafted header in a (1) MOVE or (2) COPY request, involving an authorization check.

## References
- http://lists.fedoraproject.org/pipermail/package-announce/2016-May/184545.html
- http://lists.opensuse.org/opensuse-updates/2016-05/msg00043.html
- http://lists.opensuse.org/opensuse-updates/2016-05/msg00044.html
- http://mail-archives.apache.org/mod_mbox/subversion-announce/201604.mbox/%3CCAP_GPNgJet+7_MAhomFVOXPgLtewcUw9w=k9zdPCkq5tvPxVMA%40mail.gmail.com%3E
- http://mail-archives.apache.org/mod_mbox/subversion-announce/201604.mbox/%3CCAP_GPNgfn1iKueW51EpmXzXi_URNfGNofZSgOyW1_jnSeNm5DQ%40mail.gmail.com%3E
- http://www.securityfocus.com/bid/89320
- http://www.securitytracker.com/id/1035707
- http://www.slackware.com/security/viewer.php?l=slackware-security&y=2016&m=slackware-security.417496
- https://www.oracle.com/security-alerts/cpuoct2020.html
- http://subversion.apache.org/security/CVE-2016-2168-advisory.txt
- http://www.debian.org/security/2016/dsa-3561
- https://security.gentoo.org/glsa/201610-05
