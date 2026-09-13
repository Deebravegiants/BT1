# [H] CVE-2023-34432

## Summary
Severity: High
Advisory: CVE-2023-34432
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-07-10
Source: https://osv.dev/vulnerability/CVE-2023-34432
Type: osv

## Details
A heap buffer overflow vulnerability was found in sox, in the lsx_readbuf function at sox/src/formats_i.c:98:16. This flaw can lead to a denial of service, code execution, or information disclosure.

## References
- https://access.redhat.com/security/cve/CVE-2023-34432
- https://bugzilla.redhat.com/show_bug.cgi?id=2212291
