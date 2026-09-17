# [M] CVE-2017-5851

## Summary
Severity: Medium
Advisory: CVE-2017-5851
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-01
Source: https://osv.dev/vulnerability/CVE-2017-5851
Type: osv

## Details
The free_options function in options_manager.c in mp3splt 2.6.2 allows remote attackers to cause a denial of service (NULL pointer dereference and crash) via a crafted file.  NOTE: this typically has no risk; this crash of this command-line program has no further consequences for availability.

## References
- http://www.securityfocus.com/bid/96002
- https://blogs.gentoo.org/ago/2017/02/01/mp3splt-null-pointer-dereference-in-free_options-options_manager-c/
