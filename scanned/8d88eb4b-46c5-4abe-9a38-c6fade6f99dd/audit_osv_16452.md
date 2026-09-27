# [M] CVE-2019-7146

## Summary
Severity: Medium
Advisory: CVE-2019-7146
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-01-29
Source: https://osv.dev/vulnerability/CVE-2019-7146
Type: osv

## Details
In elfutils 0.175, there is a buffer over-read in the ebl_object_note function in eblobjnote.c in libebl. Remote attackers could leverage this vulnerability to cause a denial-of-service via a crafted elf file, as demonstrated by eu-readelf.

## References
- https://access.redhat.com/errata/RHSA-2019:3575
- https://sourceware.org/bugzilla/show_bug.cgi?id=24075
- https://sourceware.org/bugzilla/show_bug.cgi?id=24081
