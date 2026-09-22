# [H] CVE-2021-36367

## Summary
Severity: High
Advisory: CVE-2021-36367
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N)
Published: 2021-07-09
Source: https://osv.dev/vulnerability/CVE-2021-36367
Type: osv

## Details
PuTTY through 0.75 proceeds with establishing an SSH session even if it has never sent a substantive authentication response. This makes it easier for an attacker-controlled SSH server to present a later spoofed authentication prompt (that the attacker can use to capture credential data, and use that data for purposes that are undesired by the client user).

## References
- https://git.tartarus.org/?p=simon/putty.git%3Ba=commit%3Bh=1dc5659aa62848f0aeb5de7bd3839fecc7debefa
- https://lists.debian.org/debian-lts-announce/2024/04/msg00016.html
- https://www.debian.org/security/2023/dsa-5588
- https://www.chiark.greenend.org.uk/~sgtatham/putty/changes.html
