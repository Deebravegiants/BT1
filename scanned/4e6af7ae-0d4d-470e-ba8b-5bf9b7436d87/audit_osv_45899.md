# [C] JLSEC-2026-456

## Summary
Severity: Critical
Advisory: JLSEC-2026-456
Ecosystem: Julia
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2026-05-07
Source: https://osv.dev/vulnerability/JLSEC-2026-456
Type: osv

## Affected
- Julia: `FreeType2_jll` — affected >=0 <2.10.4+0

## Details
Heap buffer overflow in Freetype in Google Chrome prior to 86.0.4240.111 allowed a remote attacker to potentially exploit heap corruption via a crafted HTML page.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-11/msg00016.html
- http://seclists.org/fulldisclosure/2020/Nov/33
- https://chromereleases.googleblog.com/2020/10/stable-channel-update-for-desktop_20.html
- https://crbug.com/1139963
- https://googleprojectzero.blogspot.com/p/rca-cve-2020-15999.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/J3QVIGAAJ4D62YEJAJJWMCCBCOQ6TVL7/
- https://security.gentoo.org/glsa/202011-12
- https://security.gentoo.org/glsa/202012-04
- https://security.gentoo.org/glsa/202401-19
- https://security.netapp.com/advisory/ntap-20240812-0001/
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2020-15999
- https://www.debian.org/security/2021/dsa-4824
