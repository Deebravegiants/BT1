# [M] scsi: qla1280: Fix kernel oops when debug level > 2

## Summary
Severity: Medium
Advisory: CVE-2025-21957
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-01
Source: https://osv.dev/vulnerability/CVE-2025-21957
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.24 <5.4.292, >=5.5.0 <5.10.236, >=5.11.0 <5.15.180, >=5.16.0 <6.1.132, >=6.2.0 <6.6.84, >=6.7.0 <6.12.20, >=6.13.0 <6.13.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: qla1280: Fix kernel oops when debug level > 2

A null dereference or oops exception will eventually occur when qla1280.c
driver is compiled with DEBUG_QLA1280 enabled and ql_debug_level > 2.  I
think its clear from the code that the intention here is sg_dma_len(s) not
length of sg_next(s) when printing the debug info.

## References
- https://git.kernel.org/stable/c/11a8dac1177a596648a020a7f3708257a2f95fee
- https://git.kernel.org/stable/c/24602e2664c515a4f2950d7b52c3d5997463418c
- https://git.kernel.org/stable/c/5233e3235dec3065ccc632729675575dbe3c6b8a
- https://git.kernel.org/stable/c/7ac2473e727d67a38266b2b7e55c752402ab588c
- https://git.kernel.org/stable/c/af71ba921d08c241a817010f96458dc5e5e26762
- https://git.kernel.org/stable/c/afa27b7c17a48e01546ccaad0ab017ad0496a522
- https://git.kernel.org/stable/c/c737e2a5fb7f90b96a96121da1b50a9c74ae9b8c
- https://git.kernel.org/stable/c/ea371d1cdefb0951c7127a33bcd7eb931cf44571
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21957.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21957
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
