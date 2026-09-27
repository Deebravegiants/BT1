# [H] CVE-2023-34318

## Summary
Severity: High
Advisory: CVE-2023-34318
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-07-10
Source: https://osv.dev/vulnerability/CVE-2023-34318
Type: osv

## Details
A heap buffer overflow vulnerability was found in sox, in the startread function at sox/src/hcom.c:160:41. This flaw can lead to a denial of service, code execution, or information disclosure.

## References
- https://access.redhat.com/security/cve/CVE-2023-34318
- https://bugzilla.redhat.com/show_bug.cgi?id=2212283
