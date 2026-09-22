# [H] ALPINE-CVE-2022-43995

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-43995
Ecosystem: Alpine:v3.14, Alpine:v3.15
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2022-11-02
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-43995
Type: osv

## Affected
- Alpine:v3.14: `sudo` — affected >=1.8.0 <1.9.12-r1
- Alpine:v3.15: `sudo` — affected >=1.8.0 <1.9.12-r1

## Details
Sudo 1.8.0 through 1.9.12, with the crypt() password backend, contains a plugins/sudoers/auth/passwd.c array-out-of-bounds error that can result in a heap-based buffer over-read. This can be triggered by arbitrary local users with access to Sudo by entering a password of seven characters or fewer. The impact could vary depending on the system libraries, compiler, and processor architecture.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-43995
