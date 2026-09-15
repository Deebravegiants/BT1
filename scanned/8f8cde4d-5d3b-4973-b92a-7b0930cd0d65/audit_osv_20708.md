# [H] CVE-2021-36369

## Summary
Severity: High
Advisory: CVE-2021-36369
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2022-10-12
Source: https://osv.dev/vulnerability/CVE-2021-36369
Type: osv

## Details
An issue was discovered in Dropbear through 2020.81. Due to a non-RFC-compliant check of the available authentication methods in the client-side SSH code, it is possible for an SSH server to change the login process in its favor. This attack can bypass additional security measures such as FIDO2 tokens or SSH-Askpass. Thus, it allows an attacker to abuse a forwarded agent for logging on to another server unnoticed.

## References
- https://github.com/mkj/dropbear/pull/128
- https://github.com/mkj/dropbear/releases
- https://github.com/mkj/dropbear/releases/tag/DROPBEAR_2022.82
- https://lists.debian.org/debian-lts-announce/2022/11/msg00015.html
