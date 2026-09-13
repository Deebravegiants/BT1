# [M] Improper Restriction of XML External Entity Reference in Elasticsearch

## Summary
Severity: Medium
Advisory: GHSA-ccmr-qj26-845g
CVE: CVE-2018-17247
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-ccmr-qj26-845g
Type: github-advisory

## Affected
- Maven: `org.elasticsearch:elasticsearch` — affected >=6.5.0 <6.5.2

## Details
Elasticsearch Security versions 6.5.0 and 6.5.1 contain an XXE flaw in Machine Learning's find_file_structure API. If a policy allowing external network access has been added to Elasticsearch's Java Security Manager then an attacker could send a specially crafted request capable of leaking content of local files on the Elasticsearch node. This could allow a user to access information that they should not have access to.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-17247
- https://discuss.elastic.co/t/elastic-stack-6-5-2-security-update/159594
- https://www.elastic.co/community/security
- http://www.securityfocus.com/bid/106294
