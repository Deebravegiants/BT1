# [M] CVE-2019-12973

## Summary
Severity: Medium
Advisory: CVE-2019-12973
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-06-26
Source: https://osv.dev/vulnerability/CVE-2019-12973
Type: osv

## Details
In OpenJPEG 2.3.1, there is excessive iteration in the opj_t1_encode_cblks function of openjp2/t1.c. Remote attackers could leverage this vulnerability to cause a denial of service via a crafted bmp file. This issue is similar to CVE-2018-6616.

## References
- https://github.com/uclouvain/openjpeg/pull/1185/commits/cbe7384016083eac16078b359acd7a842253d503
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00088.html
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00090.html
- http://www.securityfocus.com/bid/108900
- https://lists.debian.org/debian-lts-announce/2020/07/msg00008.html
- https://security.gentoo.org/glsa/202101-29
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://www.oracle.com/security-alerts/cpujul2020.html
- https://github.com/uclouvain/openjpeg/commit/8ee335227bbcaf1614124046aa25e53d67b11ec3
