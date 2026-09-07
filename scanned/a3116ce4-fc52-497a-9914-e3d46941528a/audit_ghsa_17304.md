# [M] Elasticsearch PKI Realm Authentication Bypass Vulnerability Allows User Impersonation Through Crafted Client Certificates

## Summary
Severity: Medium
Advisory: GHSA-m9gh-789g-q5pv
CVE: CVE-2025-37731
CWE: CWE-287, CWE-295
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-12-15
Source: https://github.com/advisories/GHSA-m9gh-789g-q5pv
Type: github-advisory

## Affected
- Maven: `org.elasticsearch:elasticsearch` — affected >=7.0.0-alpha1 <8.19.8
- Maven: `org.elasticsearch:elasticsearch` — affected >=9.0.0-beta1 <9.1.8
- Maven: `org.elasticsearch:elasticsearch` — affected >=9.2.0 <9.2.2

## Details
Improper Authentication in Elasticsearch PKI realm can lead to user impersonation via specially crafted client certificates. A malicious actor would need to have such a crafted client certificate signed by a legitimate, trusted Certificate Authority.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-37731
- https://github.com/elastic/elasticsearch/commit/cd97b8566bf56e628070021300784cb9cee0286f
- https://github.com/elastic/elasticsearch/commit/d8a408da79f214395845d99d241e832077045983
- https://github.com/elastic/elasticsearch/commit/e519fe4c51a3c887675eb7daea2f914738847f23
- https://discuss.elastic.co/t/elasticsearch-8-19-8-9-1-8-and-9-2-2-security-update-esa-2025-27/384063
- https://github.com/elastic/elasticsearch
