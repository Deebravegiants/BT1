# [H] NFS: Check the TLS certificate fields in nfs_match_client()

## Summary
Severity: High
Advisory: CVE-2025-68243
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-16
Source: https://osv.dev/vulnerability/CVE-2025-68243
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.17.0 <6.17.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

NFS: Check the TLS certificate fields in nfs_match_client()

If the TLS security policy is of type RPC_XPRTSEC_TLS_X509, then the
cert_serial and privkey_serial fields need to match as well since they
define the client's identity, as presented to the server.

## References
- https://git.kernel.org/stable/c/b8fa37219074811c04d4ecb742c73e2b296da6a8
- https://git.kernel.org/stable/c/fb2cba0854a7f315c8100a807a6959b99d72479e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68243.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68243
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
