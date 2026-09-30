# [M] Qemu: sdhci: heap buffer overflow in sdhci_write_dataport()

## Summary
Severity: Medium
Advisory: CVE-2024-3447
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:N/I:N/A:H)
Published: 2024-11-14
Source: https://osv.dev/vulnerability/CVE-2024-3447
Type: osv

## Details
A heap-based buffer overflow was found in the SDHCI device emulation of QEMU. The bug is triggered when both `s->data_count` and the size of  `s->fifo_buffer` are set to 0x200, leading to an out-of-bound access. A malicious guest could use this flaw to crash the QEMU process on the host, resulting in a denial of service condition.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=58813
- https://cert-portal.siemens.com/productcert/html/ssa-577017.html
- https://lists.debian.org/debian-lts-announce/2025/04/msg00042.html
- https://patchew.org/QEMU/20240404085549.16987-1-philmd@linaro.org/
- https://access.redhat.com/security/cve/CVE-2024-3447
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/3xxx/CVE-2024-3447.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-3447
- https://security.netapp.com/advisory/ntap-20250425-0005/
- https://bugzilla.redhat.com/show_bug.cgi?id=2274123
- https://gitlab.com/qemu-project/qemu
