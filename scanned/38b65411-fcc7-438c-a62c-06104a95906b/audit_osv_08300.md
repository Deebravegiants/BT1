# [M] CVE-2016-2165

## Summary
Severity: Medium
Advisory: CVE-2016-2165
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2017-05-25
Source: https://osv.dev/vulnerability/CVE-2016-2165
Type: osv

## Details
The Loggregator Traffic Controller endpoints in cf-release v231 and lower, Pivotal Elastic Runtime versions prior to 1.5.19 AND 1.6.x versions prior to 1.6.20 are not cleansing request URL paths when they are invalid and are returning them in the 404 response. This could allow malicious scripts to be written directly into the 404 response.

## References
- https://pivotal.io/security/cve-2016-2165
