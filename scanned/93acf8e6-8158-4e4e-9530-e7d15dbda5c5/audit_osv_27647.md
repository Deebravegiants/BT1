# [H] CVE-2024-24474

## Summary
Severity: High
Advisory: CVE-2024-24474
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-20
Source: https://osv.dev/vulnerability/CVE-2024-24474
Type: osv

## Details
QEMU before 8.2.0 has an integer underflow, and resultant buffer overflow, via a TI command when an expected non-DMA transfer length is less than the length of the available FIFO data. This occurs in esp_do_nodma in hw/scsi/esp.c because of an underflow of async_len.

## References
- https://gist.github.com/1047524396/5ce07b9d387095c276b1cd234ae5615e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/24xxx/CVE-2024-24474.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-24474
- https://security.netapp.com/advisory/ntap-20240510-0012/
- https://gitlab.com/qemu-project/qemu/-/issues/1810
- https://github.com/qemu/qemu/commit/77668e4b9bca03a856c27ba899a2513ddf52bb52
