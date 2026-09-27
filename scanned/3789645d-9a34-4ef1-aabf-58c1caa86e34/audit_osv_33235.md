# [H] smb: client: fix smbdirect_recv_io leak in smbd_negotiate() error path

## Summary
Severity: High
Advisory: CVE-2025-39929
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-04
Source: https://osv.dev/vulnerability/CVE-2025-39929
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.16.0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.154, >=6.2.0 <6.6.108, >=6.7.0 <6.12.49, >=6.13.0 <6.16.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: client: fix smbdirect_recv_io leak in smbd_negotiate() error path

During tests of another unrelated patch I was able to trigger this
error: Objects remaining on __kmem_cache_shutdown()

## References
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/0991418bf98f191d0c320bd25245fcffa1998c7e
- https://git.kernel.org/stable/c/3d7c075c878ac844e33c43e506c2fa27ac7e9689
- https://git.kernel.org/stable/c/5aa69aabcb275a8012265233c7694076ce1d9102
- https://git.kernel.org/stable/c/922338efaad63cfe30d459dfc59f9d69ff93ded4
- https://git.kernel.org/stable/c/aa4cf7615328eae44f3b4bf5f4fde3fb390c27c6
- https://git.kernel.org/stable/c/daac51c7032036a0ca5f1aa419ad1b0471d1c6e0
- https://git.kernel.org/stable/c/e7b7a93879558e77d950f1ff9a6f3daa385b33df
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39929.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39929
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
