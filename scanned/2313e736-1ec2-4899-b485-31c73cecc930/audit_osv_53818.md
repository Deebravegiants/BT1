# [M] CVE-2023-26590

## Summary
Severity: Medium
Advisory: CVE-2023-26590
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-07-10
Source: https://osv.dev/vulnerability/CVE-2023-26590
Type: osv

## Details
A floating point exception vulnerability was found in sox, in the lsx_aiffstartwrite function at sox/src/aiff.c:622:58. This flaw can lead to a denial of service.

## References
- https://access.redhat.com/security/cve/CVE-2023-26590
- https://bugzilla.redhat.com/show_bug.cgi?id=2212279
