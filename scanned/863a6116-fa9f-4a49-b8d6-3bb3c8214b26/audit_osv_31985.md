# [H] ksmbd: fix r_count dec/increment mismatch

## Summary
Severity: High
Advisory: CVE-2025-22074
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-16
Source: https://osv.dev/vulnerability/CVE-2025-22074
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.6.87, >=6.7.0 <6.12.23, >=6.13.0 <6.13.11, >=6.14.0 <6.14.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix r_count dec/increment mismatch

r_count is only increased when there is an oplock break wait,
so r_count inc/decrement are not paired. This can cause r_count
to become negative, which can lead to a problem where the ksmbd
thread does not terminate.

## References
- https://git.kernel.org/stable/c/20378cf48359f39dee0ef9b61470ebe77bd49c0d
- https://git.kernel.org/stable/c/457db486203c90e10c3efc87fd45cc7000b1cd36
- https://git.kernel.org/stable/c/4790bcb269e5d6d88200a67c54ae6d627332a3be
- https://git.kernel.org/stable/c/c2ec33d46b4d1c8085dab5d02e00b21f4f0fb8a9
- https://git.kernel.org/stable/c/ddb7ea36ba7129c2ed107e2186591128618864e1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22074.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-22074
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
