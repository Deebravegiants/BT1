# [M] CVE-2021-26247

## Summary
Severity: Medium
Advisory: CVE-2021-26247
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2022-01-19
Source: https://osv.dev/vulnerability/CVE-2021-26247
Type: osv

## Details
As an unauthenticated remote user, visit "http://<CACTI_SERVER>/auth_changepassword.php?ref=<script>alert(1)</script>" to successfully execute the JavaScript payload present in the "ref" URL parameter.

## References
- https://www.cacti.net/info/changelog
