# [C] CVE-2018-15759

## Summary
Severity: Critical
Advisory: CVE-2018-15759
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-11-19
Source: https://osv.dev/vulnerability/CVE-2018-15759
Type: osv

## Details
Pivotal Cloud Foundry On Demand Services SDK, versions prior to 0.24 contain an insecure method of verifying credentials. A remote unauthenticated malicious user may make many requests to the service broker with different credentials, allowing them to infer valid credentials and gain access to perform broker operations.

## References
- http://www.securityfocus.com/bid/106019
- https://pivotal.io/security/cve-2018-15759
