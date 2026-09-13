# [H] CVE-2023-0386

## Summary
Severity: High
Advisory: CVE-2023-0386
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-03-22
Source: https://osv.dev/vulnerability/CVE-2023-0386
Type: osv

## Details
A flaw was found in the Linux kernel, where unauthorized access to the execution of the setuid file with capabilities was found in the Linux kernel’s OverlayFS subsystem in how a user copies a capable file from a nosuid mount into another mount. This uid mapping bug allows a local user to escalate their privileges on the system.

## References
- http://packetstormsecurity.com/files/173087/Kernel-Live-Patch-Security-Notice-LSN-0095-1.html
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=4f11ada10d0a
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2023-0386
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/0xxx/CVE-2023-0386.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-0386
- https://security.netapp.com/advisory/ntap-20230420-0004/
- https://www.debian.org/security/2023/dsa-5402
- https://lists.debian.org/debian-lts-announce/2023/06/msg00008.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
