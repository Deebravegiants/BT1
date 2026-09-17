# [M] firmware_loader: Fix possible resource leak in fw_log_firmware_info()

## Summary
Severity: Medium
Advisory: CVE-2024-53202
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-53202
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.64, >=6.7.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

firmware_loader: Fix possible resource leak in fw_log_firmware_info()

The alg instance should be released under the exception path, otherwise
there may be resource leak here.

To mitigate this, free the alg instance with crypto_free_shash when kmalloc
fails.

## References
- https://git.kernel.org/stable/c/369a9c046c2fdfe037f05b43b84c386bdbccc103
- https://git.kernel.org/stable/c/789a72498d32f88d24371c10985aceb46397056c
- https://git.kernel.org/stable/c/eb5d67d00ad17a5bd0920f455160dc2ccbd2dc78
- https://git.kernel.org/stable/c/f380f895dbb2a11d62ca6df9e82d995f4bc26b84
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53202.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53202
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
