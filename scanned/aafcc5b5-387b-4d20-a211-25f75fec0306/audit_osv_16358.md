# [M] CVE-2019-6109

## Summary
Severity: Medium
Advisory: CVE-2019-6109
CVSS: 6.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:N)
Published: 2019-01-31
Source: https://osv.dev/vulnerability/CVE-2019-6109
Type: osv

## Details
An issue was discovered in OpenSSH 7.9. Due to missing character encoding in the progress display, a malicious server (or Man-in-The-Middle attacker) can employ crafted object names to manipulate the client output, e.g., by using ANSI control codes to hide additional files being transferred. This affects refresh_progress_meter() in progressmeter.c.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00058.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/W3YVQ2BPTOVDCFDVNC2GGF5P5ISFG37G/
- https://access.redhat.com/errata/RHSA-2019:3702
- https://cvsweb.openbsd.org/src/usr.bin/ssh/progressmeter.c
- https://cvsweb.openbsd.org/src/usr.bin/ssh/scp.c
- https://lists.debian.org/debian-lts-announce/2019/03/msg00030.html
- https://security.gentoo.org/glsa/201903-16
- https://security.netapp.com/advisory/ntap-20190213-0001/
- https://sintonen.fi/advisories/scp-client-multiple-vulnerabilities.txt
- https://usn.ubuntu.com/3885-1/
- https://www.debian.org/security/2019/dsa-4387
- https://cert-portal.siemens.com/productcert/pdf/ssa-412672.pdf
- https://www.oracle.com/technetwork/security-advisory/cpuoct2019-5072832.html
