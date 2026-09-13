# [M] CVE-2019-17557

## Summary
Severity: Medium
Advisory: CVE-2019-17557
Aliases: GHSA-6qj8-c27w-rp33
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N)
Published: 2020-05-04
Source: https://osv.dev/vulnerability/CVE-2019-17557
Type: osv

## Details
It was found that the Apache Syncope EndUser UI login page prio to 2.0.15 and 2.1.6 reflects the successMessage parameters. By this mean, a user accessing the Enduser UI could execute javascript code from URL query string.

## References
- http://syncope.apache.org/security
