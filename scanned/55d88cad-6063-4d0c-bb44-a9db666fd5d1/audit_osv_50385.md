# [M] CVE-2020-14373

## Summary
Severity: Medium
Advisory: CVE-2020-14373
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-09-03
Source: https://osv.dev/vulnerability/CVE-2020-14373
Type: osv

## Details
A use after free was found in igc_reloc_struct_ptr() of psi/igc.c of ghostscript-9.25. A local attacker could supply a specially crafted PDF file to cause a denial of service.

## References
- https://git.ghostscript.com/?p=ghostpdl.git%3Ba=commitdiff%3Bh=ece5cbbd9979cd35737b00e68267762d72feb2ea%3Bhp=1ef5f08f2c2e27efa978f0010669ff22355c385f
- https://bugzilla.redhat.com/show_bug.cgi?id=1873239
- https://bugs.ghostscript.com/show_bug.cgi?id=702851
