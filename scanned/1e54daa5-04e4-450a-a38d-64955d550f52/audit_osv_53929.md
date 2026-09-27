# [M] CVE-2023-32627

## Summary
Severity: Medium
Advisory: CVE-2023-32627
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-07-10
Source: https://osv.dev/vulnerability/CVE-2023-32627
Type: osv

## Details
A floating point exception vulnerability was found in sox, in the read_samples function at sox/src/voc.c:334:18. This flaw can lead to a denial of service.

## References
- https://lists.debian.org/debian-lts-announce/2023/08/msg00015.html
- https://access.redhat.com/security/cve/CVE-2023-32627
- https://bugzilla.redhat.com/show_bug.cgi?id=2212282
