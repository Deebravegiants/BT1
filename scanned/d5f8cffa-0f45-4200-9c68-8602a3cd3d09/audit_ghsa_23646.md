# [H] Incorrect Privilege Assignment in RESTEasy

## Summary
Severity: High
Advisory: GHSA-qjpq-5pq3-43rr
CVE: CVE-2014-3490
CWE: CWE-266
Ecosystem: Maven
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-qjpq-5pq3-43rr
Type: github-advisory

## Affected
- Maven: `org.jboss.resteasy:resteasy-client` — affected >=2.3.1 <2.3.8.SP2
- Maven: `org.jboss.resteasy:resteasy-client` — affected >=3.0.0 <3.0.9.Final

## Details
RESTEasy 2.3.1 before 2.3.8.SP2 and 3.x before 3.0.9, as used in Red Hat JBoss Enterprise Application Platform (EAP) 6.3.0, does not disable external entities when the resteasy.document.expand.entity.references parameter is set to false, which allows remote attackers to read arbitrary files and have other unspecified impact via unspecified vectors, related to an XML External Entity (XXE) issue.  NOTE: this vulnerability exists because of an incomplete fix for CVE-2012-0818.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-3490
- https://github.com/resteasy/Resteasy/pull/521
- https://github.com/resteasy/Resteasy/pull/533
- https://github.com/ronsigal/Resteasy/commit/9b7d0f574cafdcf3bea5428f3145ab4908fc6d83
- http://rhn.redhat.com/errata/RHSA-2014-1011.html
- http://rhn.redhat.com/errata/RHSA-2014-1039.html
- http://rhn.redhat.com/errata/RHSA-2014-1040.html
- http://rhn.redhat.com/errata/RHSA-2014-1298.html
- http://rhn.redhat.com/errata/RHSA-2015-0125.html
- http://rhn.redhat.com/errata/RHSA-2015-0675.html
- http://rhn.redhat.com/errata/RHSA-2015-0720.html
- http://rhn.redhat.com/errata/RHSA-2015-0765.html
- http://www.oracle.com/technetwork/security-advisory/cpuoct2018-4428296.html
