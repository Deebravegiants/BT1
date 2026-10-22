# [H] CVE-2019-11271

## Summary
Severity: High
Advisory: CVE-2019-11271
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-06-19
Source: https://osv.dev/vulnerability/CVE-2019-11271
Type: osv

## Details
Cloud Foundry BOSH 270.x versions prior to v270.1.1, contain a BOSH Director that does not properly redact credentials when configured to use a MySQL database. A local authenticated malicious user may read any credentials that are contained in a BOSH manifest.

## References
- https://www.cloudfoundry.org/blog/cve-2019-11271
