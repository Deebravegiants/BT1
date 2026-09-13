# [H] CVE-2021-26910

## Summary
Severity: High
Advisory: CVE-2021-26910
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-02-08
Source: https://osv.dev/vulnerability/CVE-2021-26910
Type: osv

## Details
Firejail before 0.9.64.4 allows attackers to bypass intended access restrictions because there is a TOCTOU race condition between a stat operation and an OverlayFS mount operation.

## References
- https://github.com/netblue30/firejail/releases/tag/0.9.64.4
- https://lists.debian.org/debian-lts-announce/2021/02/msg00015.html
- https://security.gentoo.org/glsa/202105-19
- https://www.debian.org/security/2021/dsa-4849
- http://www.openwall.com/lists/oss-security/2021/02/09/1
- https://github.com/netblue30/firejail/commit/97d8a03cad19501f017587cc4e47d8418273834b
- https://unparalleled.eu/blog/2021/20210208-rigged-race-against-firejail-for-local-root/
- https://unparalleled.eu/publications/2021/advisory-unpar-2021-0.txt
