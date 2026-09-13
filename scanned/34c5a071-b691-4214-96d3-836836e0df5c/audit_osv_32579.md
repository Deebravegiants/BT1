# [M] CVE-2025-32728

## Summary
Severity: Medium
Advisory: CVE-2025-32728
CVSS: 4.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:N/I:L/A:N)
Published: 2025-04-10
Source: https://osv.dev/vulnerability/CVE-2025-32728
Type: osv

## Details
In sshd in OpenSSH before 10.0, the DisableForwarding directive does not adhere to the documentation stating that it disables X11 and agent forwarding.

## References
- https://ftp.openbsd.org/pub/OpenBSD/patches/7.6/common/013_ssh.patch.sig
- https://lists.debian.org/debian-lts-announce/2025/05/msg00008.html
- https://lists.mindrot.org/pipermail/openssh-unix-dev/2025-April/041879.html
- https://www.openssh.com/txt/release-10.0
- https://www.openssh.com/txt/release-7.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/32xxx/CVE-2025-32728.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-32728
- https://security.netapp.com/advisory/ntap-20250425-0002/
- https://github.com/openssh/openssh-portable/commit/fc86875e6acb36401dfc1dfb6b628a9d1460f367
