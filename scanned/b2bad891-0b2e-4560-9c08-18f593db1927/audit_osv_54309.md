# [M] CVE-2023-47384

## Summary
Severity: Medium
Advisory: CVE-2023-47384
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-11-14
Source: https://osv.dev/vulnerability/CVE-2023-47384
Type: osv

## Details
MP4Box GPAC v2.3-DEV-rev617-g671976fcc-master was discovered to contain a memory leak in the function gf_isom_add_chapter at /isomedia/isom_write.c. This vulnerability allows attackers to cause a Denial of Service (DoS) via a crafted MP4 file.

## References
- https://github.com/gpac/gpac/issues/2672
