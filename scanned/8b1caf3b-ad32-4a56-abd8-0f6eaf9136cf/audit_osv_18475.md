# [M] CVE-2020-27839

## Summary
Severity: Medium
Advisory: CVE-2020-27839
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N)
Published: 2021-05-26
Source: https://osv.dev/vulnerability/CVE-2020-27839
Type: osv

## Details
A flaw was found in ceph-dashboard. The JSON Web Token (JWT) used for user authentication is stored by the frontend application in the browser’s localStorage which is potentially vulnerable to attackers via XSS attacks. The highest threat from this vulnerability is to data confidentiality and integrity.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1901330
