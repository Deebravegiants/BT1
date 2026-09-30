# [M] CVE-2019-7619

## Summary
Severity: Medium
Advisory: CVE-2019-7619
Aliases: GHSA-hxp8-r9g3-grfr
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2019-10-30
Source: https://osv.dev/vulnerability/CVE-2019-7619
Type: osv

## Details
Elasticsearch versions 7.0.0-7.3.2 and 6.7.0-6.8.3 contain a username disclosure flaw was found in the API Key service. An unauthenticated attacker could send a specially crafted request and determine if a username exists in the Elasticsearch native realm.

## References
- https://discuss.elastic.co/t/elastic-stack-6-8-4-security-update/204908
- https://discuss.elastic.co/t/elastic-stack-7-4-0-security-update/201831
- https://www.elastic.co/community/security
