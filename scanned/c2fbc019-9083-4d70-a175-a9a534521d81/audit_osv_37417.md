# [C] smb: server: let send_done handle a completion without IB_SEND_SIGNALED

## Summary
Severity: Critical
Advisory: CVE-2026-31536
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-31536
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.18.11, >=6.19.0 <6.19.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: server: let send_done handle a completion without IB_SEND_SIGNALED

With smbdirect_send_batch processing we likely have requests without
IB_SEND_SIGNALED, which will be destroyed in the final request
that has IB_SEND_SIGNALED set.

If the connection is broken all requests are signaled
even without explicit IB_SEND_SIGNALED.

## References
- https://git.kernel.org/stable/c/24082642654f3e5149913946e89c00a297a8868f
- https://git.kernel.org/stable/c/9da82dc73cb03e85d716a2609364572367a5ff47
- https://git.kernel.org/stable/c/e38b415c024bc3b6321bf8650dbf3f4aab8e74b3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31536.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31536
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
