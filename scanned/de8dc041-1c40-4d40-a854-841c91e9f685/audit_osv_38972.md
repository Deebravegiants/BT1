# [H] cifs: Fix locking usage for tcon fields

## Summary
Severity: High
Advisory: CVE-2026-43215
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-43215
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.6.128, >=6.7.0 <6.12.75, >=6.13.0 <6.18.16, >=6.19.0 <6.19.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

cifs: Fix locking usage for tcon fields

We used to use the cifs_tcp_ses_lock to protect a lot of objects
that are not just the server, ses or tcon lists. We later introduced
srv_lock, ses_lock and tc_lock to protect fields within the
corresponding structs. This was done to provide a more granular
protection and avoid unnecessary serialization.

There were still a couple of uses of cifs_tcp_ses_lock to provide
tcon fields. In this patch, I've replaced them with tc_lock.

## References
- https://git.kernel.org/stable/c/3969db6b22e3d90d8c5f22ac1a7fe0350a94c136
- https://git.kernel.org/stable/c/601dd3b79769b38d30b693c40afdb2a4b7edf9d0
- https://git.kernel.org/stable/c/8c59eeeeffa1524ef57e173a89a1a3ff539888d5
- https://git.kernel.org/stable/c/953953abb66e52c224057ab91e404284fefeab62
- https://git.kernel.org/stable/c/96c4af418586ee9a6aab61738644366426e05316
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43215.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43215
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
