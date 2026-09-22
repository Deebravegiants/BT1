# [H] CVE-2017-10683

## Summary
Severity: High
Advisory: CVE-2017-10683
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-06-29
Source: https://osv.dev/vulnerability/CVE-2017-10683
Type: osv

## Details
In mpg123 1.25.0, there is a heap-based buffer over-read in the convert_latin1 function in libmpg123/id3.c. A crafted input will lead to a remote denial of service attack.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1465819
