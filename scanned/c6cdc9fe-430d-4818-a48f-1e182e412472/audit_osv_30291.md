# [H] ksmbd: check outstanding simultaneous SMB operations

## Summary
Severity: High
Advisory: CVE-2024-50285
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-50285
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.6.61, >=6.7.0 <6.11.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: check outstanding simultaneous SMB operations

If Client send simultaneous SMB operations to ksmbd, It exhausts too much
memory through the "ksmbd_work_cache”. It will cause OOM issue.
ksmbd has a credit mechanism but it can't handle this problem. This patch
add the check if it exceeds max credits to prevent this problem by assuming
that one smb request consumes at least one credit.

## References
- https://git.kernel.org/stable/c/0a77d947f599b1f39065015bec99390d0c0022ee
- https://git.kernel.org/stable/c/1f993777275cbd8f74765c4f9d9285cb907c9be5
- https://git.kernel.org/stable/c/e257ac6fe138623cf59fca8898abdf659dbc8356
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50285.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50285
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
