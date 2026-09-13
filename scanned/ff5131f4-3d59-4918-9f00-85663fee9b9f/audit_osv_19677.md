# [C] CVE-2021-23592

## Summary
Severity: Critical
Advisory: CVE-2021-23592
Aliases: GHSA-3fpv-54ff-wqfj
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-05-06
Source: https://osv.dev/vulnerability/CVE-2021-23592
Type: osv

## Details
The package topthink/framework before 6.0.12 are vulnerable to Deserialization of Untrusted Data due to insecure unserialize method in the Driver class.

## References
- https://github.com/top-think/framework/releases/tag/v6.0.12
- https://snyk.io/vuln/SNYK-PHP-TOPTHINKFRAMEWORK-2385695
- https://github.com/top-think/framework/commit/d3b5aeae94bc71bae97977d05cd12c3e0550905c
