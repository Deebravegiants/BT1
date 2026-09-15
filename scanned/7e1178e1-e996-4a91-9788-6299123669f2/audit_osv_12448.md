# [M] CVE-2018-12108

## Summary
Severity: Medium
Advisory: CVE-2018-12108
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-06-11
Source: https://osv.dev/vulnerability/CVE-2018-12108
Type: osv

## Details
An issue was discovered in Dropbox Lepton 1.2.1. The validateAndCompress function in validation.cc allows remote attackers to cause a denial of service (SIGFPE and application crash) via a malformed file.

## References
- https://github.com/dropbox/lepton/issues/107
