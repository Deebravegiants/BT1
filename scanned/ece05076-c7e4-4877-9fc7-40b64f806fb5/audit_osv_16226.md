# [H] CVE-2019-3785

## Summary
Severity: High
Advisory: CVE-2019-3785
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2019-03-13
Source: https://osv.dev/vulnerability/CVE-2019-3785
Type: osv

## Details
Cloud Foundry Cloud Controller, versions prior to 1.78.0, contain an endpoint with improper authorization. A remote authenticated malicious user with read permissions can request package information and receive a signed bit-service url that grants the user write permissions to the bit-service.

## References
- http://www.securityfocus.com/bid/107514
- https://www.cloudfoundry.org/blog/cve-2019-3785
