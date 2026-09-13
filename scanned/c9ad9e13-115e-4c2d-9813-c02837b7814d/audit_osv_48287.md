# [M] CVE-2017-5665

## Summary
Severity: Medium
Advisory: CVE-2017-5665
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-01
Source: https://osv.dev/vulnerability/CVE-2017-5665
Type: osv

## Details
The splt_cue_export_to_file function in cue.c in libmp3splt 0.9.2 allows remote attackers to cause a denial of service (NULL pointer dereference and crash) via a crafted file.

## References
- http://www.securityfocus.com/bid/95906
- https://blogs.gentoo.org/ago/2017/01/29/mp3splt-null-pointer-dereference-in-splt_cue_export_to_file-cue-c/
