# [M] CVE-2021-46920

## Summary
Severity: Medium
Advisory: CVE-2021-46920
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2024-02-27
Source: https://osv.dev/vulnerability/CVE-2021-46920
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

dmaengine: idxd: Fix clobbering of SWERR overflow bit on writeback

Current code blindly writes over the SWERR and the OVERFLOW bits. Write
back the bits actually read instead so the driver avoids clobbering the
OVERFLOW bit that comes after the register is read.

## References
- https://git.kernel.org/stable/c/02981a44a0e402089775416371bd2e0c935685f8
- https://git.kernel.org/stable/c/a5ad12d5d69c63af289a37f05187a0c6fe93553d
- https://git.kernel.org/stable/c/ea941ac294d75d0ace50797aebf0056f6f8f7a7f
