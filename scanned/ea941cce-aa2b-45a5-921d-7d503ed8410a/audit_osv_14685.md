# [C] CVE-2019-10758

## Summary
Severity: Critical
Advisory: CVE-2019-10758
Aliases: GHSA-h47j-hc6x-h3qq, SNYK-JS-MONGOEXPRESS-473215
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2019-12-24
Source: https://osv.dev/vulnerability/CVE-2019-10758
Type: osv

## Details
mongo-express before 0.54.0 is vulnerable to Remote Code Execution via endpoints that uses the `toBSON` method. A misuse of the `vm` dependency to perform `exec` commands in a non-safe environment.

## References
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2019-10758
- https://snyk.io/vuln/SNYK-JS-MONGOEXPRESS-473215
