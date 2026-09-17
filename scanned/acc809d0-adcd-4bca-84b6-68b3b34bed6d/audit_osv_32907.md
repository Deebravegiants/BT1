# [C] nvme-tcp: sanitize request list handling

## Summary
Severity: Critical
Advisory: CVE-2025-38264
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-09
Source: https://osv.dev/vulnerability/CVE-2025-38264
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.0.0 <6.12.36, >=6.13.0 <6.15.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

nvme-tcp: sanitize request list handling

Validate the request in nvme_tcp_handle_r2t() to ensure it's not part of
any list, otherwise a malicious R2T PDU might inject a loop in request
list processing.

## References
- https://git.kernel.org/stable/c/0bf04c874fcb1ae46a863034296e4b33d8fbd66c
- https://git.kernel.org/stable/c/78a4adcd3fedb0728436e8094848ebf4c6bae006
- https://git.kernel.org/stable/c/f054ea62598197714a6ca7b3b387a027308f8b13
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38264.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38264
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
