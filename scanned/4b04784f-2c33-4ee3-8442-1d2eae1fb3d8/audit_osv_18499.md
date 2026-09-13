# [H] CVE-2020-28012

## Summary
Severity: High
Advisory: CVE-2020-28012
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-05-06
Source: https://osv.dev/vulnerability/CVE-2020-28012
Type: osv

## Details
Exim 4 before 4.94.2 allows Exposure of File Descriptor to Unintended Control Sphere because rda_interpret uses a privileged pipe that lacks a close-on-exec flag.

## References
- https://www.exim.org/static/doc/security/CVE-2020-qualys/CVE-2020-28012-CLOSE.txt
