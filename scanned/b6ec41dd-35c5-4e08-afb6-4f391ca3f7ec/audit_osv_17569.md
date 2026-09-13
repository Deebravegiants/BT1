# [M] CVE-2020-1696

## Summary
Severity: Medium
Advisory: CVE-2020-1696
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N)
Published: 2020-03-20
Source: https://osv.dev/vulnerability/CVE-2020-1696
Type: osv

## Details
A flaw was found in the all pki-core 10.x.x versions, where Token Processing Service (TPS) where it did not properly sanitize Profile IDs, enabling a Stored Cross-Site Scripting (XSS) vulnerability when the profile ID is printed. An attacker with sufficient permissions could trick an authenticated victim into executing a specially crafted Javascript code.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-1696
