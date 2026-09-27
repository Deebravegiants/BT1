# [M] CVE-2021-33178

## Summary
Severity: Medium
Advisory: CVE-2021-33178
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:H)
Published: 2021-10-14
Source: https://osv.dev/vulnerability/CVE-2021-33178
Type: osv

## Details
The Manage Backgrounds functionality within NagVis versions prior to 1.9.29 is vulnerable to an authenticated path traversal vulnerability. Exploitation of this results in a malicious actor having the ability to arbitrarily delete files on the local system.

## References
- https://lists.debian.org/debian-lts-announce/2025/05/msg00000.html
- https://nagvis.org/downloads/changelog/1.9.29
- https://www.synopsys.com/blogs/software-security/cyrc-advisory-nagios-xi
