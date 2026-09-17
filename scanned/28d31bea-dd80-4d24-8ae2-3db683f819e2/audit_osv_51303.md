# [H] CVE-2021-28216

## Summary
Severity: High
Advisory: CVE-2021-28216
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-08-05
Source: https://osv.dev/vulnerability/CVE-2021-28216
Type: osv

## Details
BootPerformanceTable pointer is read from an NVRAM variable in PEI. Recommend setting PcdFirmwarePerformanceDataTableS3Support to FALSE.

## References
- https://lists.debian.org/debian-lts-announce/2025/06/msg00007.html
- https://bugzilla.tianocore.org/show_bug.cgi?id=2957
