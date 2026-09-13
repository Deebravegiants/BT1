# [H] CVE-2021-3621

## Summary
Severity: High
Advisory: CVE-2021-3621
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-12-23
Source: https://osv.dev/vulnerability/CVE-2021-3621
Type: osv

## Details
A flaw was found in SSSD, where the sssctl command was vulnerable to shell command injection via the logs-fetch and cache-expire subcommands. This flaw allows an attacker to trick the root user into running a specially crafted sssctl command, such as via sudo, to gain root access. The highest threat from this vulnerability is to confidentiality, integrity, as well as system availability.

## References
- https://lists.debian.org/debian-lts-announce/2025/02/msg00008.html
- https://lists.debian.org/debian-lts-announce/2023/05/msg00028.html
- https://sssd.io/release-notes/sssd-2.6.0.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1975142
