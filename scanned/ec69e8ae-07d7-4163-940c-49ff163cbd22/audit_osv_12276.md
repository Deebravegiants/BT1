# [H] CVE-2018-11206

## Summary
Severity: High
Advisory: CVE-2018-11206
CVSS: 8.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2018-05-16
Source: https://osv.dev/vulnerability/CVE-2018-11206
Type: osv

## Details
An out of bounds read was discovered in H5O_fill_new_decode and H5O_fill_old_decode in H5Ofill.c in the HDF HDF5 1.10.2 library. It could allow a remote denial of service or information disclosure attack.

## References
- https://lists.debian.org/debian-lts-announce/2023/08/msg00009.html
- https://github.com/TeamSeri0us/pocs/blob/master/hdf5/README2.md
- https://github.com/Twi1ight/fuzzing-pocs/tree/master/hdf5
