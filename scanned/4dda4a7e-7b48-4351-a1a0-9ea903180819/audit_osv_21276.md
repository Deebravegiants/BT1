# [H] CVE-2021-41617

## Summary
Severity: High
Advisory: CVE-2021-41617
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-09-26
Source: https://osv.dev/vulnerability/CVE-2021-41617
Type: osv

## Details
sshd in OpenSSH 6.2 through 8.x before 8.8, when certain non-default configurations are used, allows privilege escalation because supplemental groups are not initialized as expected. Helper programs for AuthorizedKeysCommand and AuthorizedPrincipalsCommand may run with privileges associated with group memberships of the sshd process, if the configuration specifies running the command as a different user.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://lists.debian.org/debian-lts-announce/2023/12/msg00017.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6XJIONMHMKZDTMH6BQR5TNLF2WDCGWED/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/KVI7RWM2JLNMWTOFK6BDUSGNOIPZYPUT/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/W44V2PFQH5YLRN6ZJTVRKAD7CU6CYYET/
- https://www.tenable.com/plugins/nessus/154174
- https://security.netapp.com/advisory/ntap-20211014-0004/
- https://www.debian.org/security/2023/dsa-5586
- https://www.openssh.com/security.html
- https://www.openssh.com/txt/release-8.8
- https://www.openwall.com/lists/oss-security/2021/09/26/1
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://www.starwindsoftware.com/security/sw-20220805-0001/
- https://bugzilla.suse.com/show_bug.cgi?id=1190975
- https://www.oracle.com/security-alerts/cpuapr2022.html
