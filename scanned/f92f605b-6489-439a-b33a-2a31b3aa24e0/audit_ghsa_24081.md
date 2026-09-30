# [M] Exposure of Sensitive Information to an Unauthorized Actor in RESTEasy

## Summary
Severity: Medium
Advisory: GHSA-wrrh-g7h3-gqmx
CVE: CVE-2012-0818
CWE: CWE-200
Ecosystem: Maven
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-wrrh-g7h3-gqmx
Type: github-advisory

## Affected
- Maven: `org.jboss.resteasy:resteasy-client` — affected >=0 <2.3.1

## Details
RESTEasy before 2.3.1 allows remote attackers to read arbitrary files via an external entity reference in a DOM document, aka an XML external entity (XXE) injection attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-0818
- https://github.com/resteasy/resteasy/commit/71ace879cf92d323bfa4d3e88db0c3059109bbf6
- https://web.archive.org/web/20200229045254/https://www.securityfocus.com/bid/51766
- https://web.archive.org/web/20200229044434/http://www.securityfocus.com/bid/51748
- https://issues.jboss.org/browse/RESTEASY-637
- https://github.com/resteasy/Resteasy
- https://exchange.xforce.ibmcloud.com/vulnerabilities/72808
- https://bugzilla.redhat.com/show_bug.cgi?id=785631
- https://access.redhat.com/security/cve/CVE-2012-0818
- https://access.redhat.com/errata/RHSA-2014:0372
- https://access.redhat.com/errata/RHSA-2014:0371
- https://access.redhat.com/errata/RHSA-2013:1263
- https://access.redhat.com/errata/RHSA-2012:1125
- https://access.redhat.com/errata/RHSA-2012:1059
- https://access.redhat.com/errata/RHSA-2012:1058
- https://access.redhat.com/errata/RHSA-2012:1057
- https://access.redhat.com/errata/RHSA-2012:1056
- https://access.redhat.com/errata/RHSA-2012:0519
- https://access.redhat.com/errata/RHSA-2012:0441
- https://access.redhat.com/errata/RHSA-2012:0421
