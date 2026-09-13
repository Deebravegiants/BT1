# [C] cifs: Fix oops due to uninitialised variable

## Summary
Severity: Critical
Advisory: CVE-2025-38737
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-05
Source: https://osv.dev/vulnerability/CVE-2025-38737
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.44, >=6.13.0 <6.16.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

cifs: Fix oops due to uninitialised variable

Fix smb3_init_transform_rq() to initialise buffer to NULL before calling
netfs_alloc_folioq_buffer() as netfs assumes it can append to the buffer it
is given.  Setting it to NULL means it should start a fresh buffer, but the
value is currently undefined.

## References
- https://git.kernel.org/stable/c/453a6d2a68e54a483d67233c6e1e24c4095ee4be
- https://git.kernel.org/stable/c/4931fe2dbe1cc0e7d350a4b51b0b330e43971d98
- https://git.kernel.org/stable/c/6adaa9fae36f848afa7278945d725e197e33c496
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38737.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38737
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
