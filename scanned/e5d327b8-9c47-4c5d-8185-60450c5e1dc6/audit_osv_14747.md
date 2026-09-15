# [M] CVE-2019-11268

## Summary
Severity: Medium
Advisory: CVE-2019-11268
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2019-07-11
Source: https://osv.dev/vulnerability/CVE-2019-11268
Type: osv

## Details
Cloud Foundry UAA version prior to 73.3.0, contain endpoints that contains improper escaping. An authenticated malicious user with basic read privileges for one identity zone can extend those reading privileges to all other identity zones and obtain private information on users, clients, and groups in all other identity zones.

## References
- https://www.cloudfoundry.org/blog/cve-2019-11268
