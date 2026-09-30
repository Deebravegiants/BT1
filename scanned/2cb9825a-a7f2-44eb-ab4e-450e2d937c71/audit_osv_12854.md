# [H] CVE-2018-15755

## Summary
Severity: High
Advisory: CVE-2018-15755
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-10-12
Source: https://osv.dev/vulnerability/CVE-2018-15755
Type: osv

## Details
Cloud Foundry CF Networking Release, versions 2.11.0 prior to 2.16.0, contain an internal api endpoint vulnerable to SQL injection between Diego cells and the policy server. A remote authenticated malicious user with mTLS certs can issue arbitrary SQL queries and gain access to the policy server.

## References
- https://www.cloudfoundry.org/blog/cve-2018-15755/
