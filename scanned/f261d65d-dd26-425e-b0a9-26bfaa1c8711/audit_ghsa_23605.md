# [M] Apache Sling POST Servlets Denial of Service Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-342c-f869-5m44
CVE: CVE-2012-2138
CWE: CWE-400
Ecosystem: Maven
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-342c-f869-5m44
Type: github-advisory

## Affected
- Maven: `org.apache.sling:org.apache.sling.servlets.post` — affected >=0 <2.1.2

## Details
The `@CopyFrom` operation in the POST servlet in the `org.apache.sling.servlets.post` bundle before 2.1.2 in Apache Sling does not prevent attempts to copy an ancestor node to a descendant node, which allows remote attackers to cause a denial of service (infinite loop) via a crafted HTTP request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-2138
- https://github.com/apache/sling-org-apache-sling-servlets-post/commit/0205892908d6ea755645be5fc16e9df53e2e7261
- https://issues.apache.org/jira/browse/SLING-2517
- http://mail-archives.apache.org/mod_mbox/www-announce/201207.mbox/%3CCAEWfVJ=PwoQmwJg0KmbrC17Gw51kgfKRsqgy=4RpMQsdGh0bVg@mail.gmail.com%3E
- http://svn.apache.org/viewvc?view=revision&revision=1352865
