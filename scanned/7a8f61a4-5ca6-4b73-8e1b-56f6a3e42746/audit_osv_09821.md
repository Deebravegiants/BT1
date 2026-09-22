# [H] CVE-2017-11590

## Summary
Severity: High
Advisory: CVE-2017-11590
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-07-24
Source: https://osv.dev/vulnerability/CVE-2017-11590
Type: osv

## Details
There is a NULL pointer dereference in the caseless_hash function in gxps-archive.c in libgxps 0.2.5. A crafted input will lead to a remote denial of service attack.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1473167
