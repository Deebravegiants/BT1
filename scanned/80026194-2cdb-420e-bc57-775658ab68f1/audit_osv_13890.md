# [M] CVE-2018-3826

## Summary
Severity: Medium
Advisory: CVE-2018-3826
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-09-19
Source: https://osv.dev/vulnerability/CVE-2018-3826
Type: osv

## Details
In Elasticsearch versions 6.0.0-beta1 to 6.2.4 a disclosure flaw was found in the _snapshot API. When the access_key and security_key parameters are set using the _snapshot API they can be exposed as plain text by users able to query the _snapshot API.

## References
- https://discuss.elastic.co/t/elastic-stack-6-3-0-and-5-6-10-security-update/135777
- https://www.elastic.co/community/security
