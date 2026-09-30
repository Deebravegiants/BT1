# [M] iavf: Fix handling of dummy receive descriptors

## Summary
Severity: Medium
Advisory: CVE-2022-49583
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49583
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.3.0 <5.4.208, >=5.5.0 <5.10.134, >=5.11.0 <5.15.58, >=5.16.0 <5.18.15

## Details
In the Linux kernel, the following vulnerability has been resolved:

iavf: Fix handling of dummy receive descriptors

Fix memory leak caused by not handling dummy receive descriptor properly.
iavf_get_rx_buffer now sets the rx_buffer return value for dummy receive
descriptors. Without this patch, when the hardware writes a dummy
descriptor, iavf would not free the page allocated for the previous receive
buffer. This is an unlikely event but can still happen.

[Jesse: massaged commit message]

## References
- https://git.kernel.org/stable/c/2918419c06088f6709ceb543feb01752779ade4c
- https://git.kernel.org/stable/c/6edb818732fc05fda495f5b3a749bd1cee01398b
- https://git.kernel.org/stable/c/a9f49e0060301a9bfebeca76739158d0cf91cdf6
- https://git.kernel.org/stable/c/c6af94324911ef0846af1a5ce5e049ca736db34b
- https://git.kernel.org/stable/c/d88d59faf4e6f9cc4767664206afdb999b10ec77
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49583.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49583
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
