# [C] smb: client: let recv_done verify data_offset, data_length and remaining_data_length

## Summary
Severity: Critical
Advisory: CVE-2025-39933
Ecosystem: Linux
CVSS: 9.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:H)
Published: 2025-10-04
Source: https://osv.dev/vulnerability/CVE-2025-39933
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.16.0 <6.16.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: client: let recv_done verify data_offset, data_length and remaining_data_length

This is inspired by the related server fixes.

## References
- https://git.kernel.org/stable/c/581fb78e0388b78911b0c920e4073737090c8b5f
- https://git.kernel.org/stable/c/f57e53ea252363234f86674db475839e5b87102e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39933.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39933
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
