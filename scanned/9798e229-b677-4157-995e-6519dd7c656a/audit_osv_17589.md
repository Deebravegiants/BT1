# [M] CVE-2020-17380

## Summary
Severity: Medium
Advisory: CVE-2020-17380
CVSS: 6.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:L)
Published: 2021-01-30
Source: https://osv.dev/vulnerability/CVE-2020-17380
Type: osv

## Details
A heap-based buffer overflow was found in QEMU through 5.0.0 in the SDHCI device emulation support. It could occur while doing a multi block SDMA transfer via the sdhci_sdma_transfer_multi_blocks() routine in hw/sd/sdhci.c. A guest user or process could use this flaw to crash the QEMU process on the host, resulting in a denial of service condition, or potentially execute arbitrary code with privileges of the QEMU process on the host.

## References
- https://lists.debian.org/debian-lts-announce/2021/04/msg00009.html
- https://security.netapp.com/advisory/ntap-20210312-0003/
- http://www.openwall.com/lists/oss-security/2021/03/09/1
- https://bugzilla.redhat.com/show_bug.cgi?id=1862167
- https://lists.nongnu.org/archive/html/qemu-devel/2020-09/msg01175.html
