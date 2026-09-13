# [C] CVE-2017-5206

## Summary
Severity: Critical
Advisory: CVE-2017-5206
CVSS: 9.0 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2017-03-23
Source: https://osv.dev/vulnerability/CVE-2017-5206
Type: osv

## Details
Firejail before 0.9.44.4, when running on a Linux kernel before 4.8, allows context-dependent attackers to bypass a seccomp-based sandbox protection mechanism via the --allow-debuggers argument.

## References
- http://www.securityfocus.com/bid/97120
- https://blog.lizzie.io/linux-containers-in-500-loc.html#fn.51
- https://firejail.wordpress.com/download-2/release-notes/
- http://www.openwall.com/lists/oss-security/2017/01/07/5
- https://github.com/netblue30/firejail/commit/6b8dba29d73257311564ee7f27b9b14758cc693e
- https://security.gentoo.org/glsa/201701-62
