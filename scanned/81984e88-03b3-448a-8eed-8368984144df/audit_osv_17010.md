# [M] CVE-2020-11089

## Summary
Severity: Medium
Advisory: CVE-2020-11089
Aliases: GHSA-hfc7-c5gv-8c2h
CVSS: 5.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:L)
Published: 2020-05-29
Source: https://osv.dev/vulnerability/CVE-2020-11089
Type: osv

## Details
In FreeRDP before 2.1.0, there is an out-of-bound read in irp functions (parallel_process_irp_create, serial_process_irp_create, drive_process_irp_write, printer_process_irp_write, rdpei_recv_pdu, serial_process_irp_write). This has been fixed in 2.1.0.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00080.html
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-hfc7-c5gv-8c2h
- https://lists.debian.org/debian-lts-announce/2023/10/msg00008.html
- https://github.com/FreeRDP/FreeRDP/commit/6b485b146a1b9d6ce72dfd7b5f36456c166e7a16
- https://github.com/FreeRDP/FreeRDP/commit/795842f4096501fcefc1a7f535ccc8132feb31d7
