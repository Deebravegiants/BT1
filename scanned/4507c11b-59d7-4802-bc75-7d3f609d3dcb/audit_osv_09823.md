# [H] CVE-2017-11592

## Summary
Severity: High
Advisory: CVE-2017-11592
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-07-24
Source: https://osv.dev/vulnerability/CVE-2017-11592
Type: osv

## Details
There is a Mismatched Memory Management Routines vulnerability in the Exiv2::FileIo::seek function of Exiv2 0.26 that will lead to a remote denial of service attack (heap memory corruption) via crafted input.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1473889
