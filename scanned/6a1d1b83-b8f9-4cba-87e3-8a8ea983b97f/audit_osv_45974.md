# [M] JLSEC-2026-533

## Summary
Severity: Medium
Advisory: JLSEC-2026-533
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/JLSEC-2026-533
Type: osv

## Affected
- Julia: `OpenJpeg_jll` — affected >=0 <2.4.0+0

## Details
In OpenJPEG 2.3.1, there is excessive iteration in the `opj_t1_encode_cblks` function of `openjp2/t1.c`. Remote attackers could leverage this vulnerability to cause a denial of service via a crafted bmp file. This issue is similar to CVE-2018-6616.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00088.html
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00090.html
- http://www.securityfocus.com/bid/108900
- https://github.com/uclouvain/openjpeg/commit/8ee335227bbcaf1614124046aa25e53d67b11ec3
- https://github.com/uclouvain/openjpeg/pull/1185/commits/cbe7384016083eac16078b359acd7a842253d503
- https://lists.debian.org/debian-lts-announce/2020/07/msg00008.html
- https://security.gentoo.org/glsa/202101-29
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://www.oracle.com/security-alerts/cpujul2020.html
