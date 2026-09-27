# [H] Insecure Deserialization in Apache Commons Collection

## Summary
Severity: High
Advisory: GHSA-6hgm-866r-3cjv
CVE: CVE-2015-6420
CWE: CWE-502
Ecosystem: Maven
Published: 2020-06-15
Source: https://github.com/advisories/GHSA-6hgm-866r-3cjv
Type: github-advisory

## Affected
- Maven: `org.apache.commons:commons-collections4` — affected >=0 <4.1
- Maven: `commons-collections:commons-collections` — affected >=0 <3.2.2
- Maven: `net.sourceforge.collections:collections-generic` — affected >=0
- Maven: `org.apache.servicemix.bundles:org.apache.servicemix.bundles.collections-generic` — affected >=0
- Maven: `org.apache.servicemix.bundles:org.apache.servicemix.bundles.commons-collections` — affected >=0

## Details
Serialized-object interfaces in Java applications using the Apache Commons Collections (ACC) library may allow remote attackers to execute arbitrary commands via a crafted serialized Java object.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-6420
- https://arxiv.org/pdf/2306.05534
- https://github.com/apache/commons-collections
- https://h20566.www2.hpe.com/portal/site/hpsc/public/kb/docDisplay?docId=emr_na-c05376917
- https://h20566.www2.hpe.com/portal/site/hpsc/public/kb/docDisplay?docId=emr_na-c05390722
- https://lists.apache.org/thread.html/r352e40ca9874d1beb4ad95403792adca7eb295e6bc3bd7b65fabcc21@%3Ccommits.samza.apache.org%3E
- https://www.kb.cert.org/vuls/id/581311
- https://www.tenable.com/security/research/tra-2017-14
- https://www.tenable.com/security/research/tra-2017-23
- http://tools.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-20151209-java-deserialization
- http://www.oracle.com/technetwork/security-advisory/cpujul2018-4258247.html
- http://www.securityfocus.com/bid/78872
