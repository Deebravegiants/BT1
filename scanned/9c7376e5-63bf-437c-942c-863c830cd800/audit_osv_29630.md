# [H] memcg_write_event_control(): fix a user-triggerable oops

## Summary
Severity: High
Advisory: CVE-2024-45021
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-09-11
Source: https://osv.dev/vulnerability/CVE-2024-45021
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.34 <4.19.321, >=4.20.0 <5.4.283, >=5.5.0 <5.10.225, >=5.11.0 <5.15.166, >=5.16.0 <6.1.107, >=6.2.0 <6.6.48, >=6.7.0 <6.10.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

memcg_write_event_control(): fix a user-triggerable oops

we are *not* guaranteed that anything past the terminating NUL
is mapped (let alone initialized with anything sane).

## References
- https://git.kernel.org/stable/c/046667c4d3196938e992fba0dfcde570aa85cd0e
- https://git.kernel.org/stable/c/0fbe2a72e853a1052abe9bc2b7df8ddb102da227
- https://git.kernel.org/stable/c/1b37ec85ad95b612307627758c6018cd9d92cca8
- https://git.kernel.org/stable/c/21b578f1d599edb87462f11113c5b0fc7a04ac61
- https://git.kernel.org/stable/c/43768fa80fd192558737e24ed6548f74554611d7
- https://git.kernel.org/stable/c/ad149f5585345e383baa65f1539d816cd715fd3b
- https://git.kernel.org/stable/c/f1aa7c509aa766080db7ab3aec2e31b1df09e57c
- https://git.kernel.org/stable/c/fa5bfdf6cb5846a00e712d630a43e3cf55ccb411
- https://lists.debian.org/debian-lts-announce/2024/10/msg00003.html
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45021.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-45021
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
