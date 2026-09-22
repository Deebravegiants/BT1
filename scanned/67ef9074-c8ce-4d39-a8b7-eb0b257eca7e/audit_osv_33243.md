# [H] ksmbd: smbdirect: verify remaining_data_length respects max_fragmented_recv_size

## Summary
Severity: High
Advisory: CVE-2025-39942
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-04
Source: https://osv.dev/vulnerability/CVE-2025-39942
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.1.154, >=6.2.0 <6.6.108, >=6.7.0 <6.12.49, >=6.13.0 <6.16.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: smbdirect: verify remaining_data_length respects max_fragmented_recv_size

This is inspired by the check for data_offset + data_length.

## References
- https://git.kernel.org/stable/c/196a3a7676d726ee67621ea2bf3b7815ac2685b4
- https://git.kernel.org/stable/c/9644798294c7287e65a7b26e35aa6d2ce3345bcc
- https://git.kernel.org/stable/c/c64b915bb3d9339adcae5db4be2c35ffbef5e615
- https://git.kernel.org/stable/c/d3cb3f209d35c44b7ee74f77ed27ebb28995b9ce
- https://git.kernel.org/stable/c/e1868ba37fd27c6a68e31565402b154beaa65df0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39942.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39942
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
