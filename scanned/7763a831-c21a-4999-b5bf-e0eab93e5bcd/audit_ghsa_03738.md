# [H] XML External Entity (XXE) Injection in Apache Solr

## Summary
Severity: High
Advisory: GHSA-3gm7-v7vw-866c
CVE: CVE-2019-0193
CWE: CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H/E:H (CVSS_V3)
Published: 2019-08-01
Source: https://github.com/advisories/GHSA-3gm7-v7vw-866c
Type: github-advisory

## Affected
- Maven: `org.apache.solr:solr-core` — affected >=0 <8.2.0

## Details
In Apache Solr, the DataImportHandler, an optional but popular module to pull in data from databases and other sources, has a feature in which the whole DIH configuration can come from a request's "dataConfig" parameter. The debug mode of the DIH admin screen uses this to allow convenient debugging / development of a DIH config. Since a DIH config can contain scripts, this parameter is a security risk. Starting with version 8.2.0 of Solr, use of this parameter requires setting the Java System property "enable.dih.dataConfigParam" to true.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-0193
- https://github.com/apache/lucene-solr/commit/02c693f3713add1b4891cbaa87127de3a55c10f7
- https://github.com/apache/lucene-solr
- https://lists.apache.org/thread.html/r19d23e8640236a3058b4d6c23e5cd663fde182255f5a9d63e0606a66@%3Cdev.lucene.apache.org%3E
- https://lists.apache.org/thread.html/r1d4a247329a8478073163567bbc8c8cb6b49c6bfc2bf58153a857af1%40%3Ccommits.druid.apache.org%3E
- https://lists.apache.org/thread.html/r1d4a247329a8478073163567bbc8c8cb6b49c6bfc2bf58153a857af1@%3Ccommits.druid.apache.org%3E
- https://lists.apache.org/thread.html/r339865b276614661770c909be1dd7e862232e3ef0af98bfd85686b51%40%3Cdev.lucene.apache.org%3E
- https://lists.apache.org/thread.html/r339865b276614661770c909be1dd7e862232e3ef0af98bfd85686b51@%3Cdev.lucene.apache.org%3E
- https://lists.apache.org/thread.html/r33aed7ad4ee9833c4190a44e2b106efd2deb19504b85e012175540f6%40%3Cissues.lucene.apache.org%3E
- https://lists.apache.org/thread.html/r33aed7ad4ee9833c4190a44e2b106efd2deb19504b85e012175540f6@%3Cissues.lucene.apache.org%3E
- https://lists.apache.org/thread.html/r3da74965aba2b5f5744b7289ad447306eeb2940c872801819faa9314%40%3Cusers.solr.apache.org%3E
- https://lists.apache.org/thread.html/r3da74965aba2b5f5744b7289ad447306eeb2940c872801819faa9314@%3Cusers.solr.apache.org%3E
- https://lists.apache.org/thread.html/r95df34bb158375948da82b4dfe9a1b5d528572d586584162f8f5aeef%40%3Cusers.solr.apache.org%3E
- https://lists.apache.org/thread.html/r95df34bb158375948da82b4dfe9a1b5d528572d586584162f8f5aeef@%3Cusers.solr.apache.org%3E
- https://lists.apache.org/thread.html/rb34d820c21f1708c351f9035d6bc7daf80bfb6ef99b34f7af1d2f699%40%3Cissues.lucene.apache.org%3E
- https://lists.apache.org/thread.html/rb34d820c21f1708c351f9035d6bc7daf80bfb6ef99b34f7af1d2f699@%3Cissues.lucene.apache.org%3E
- https://lists.apache.org/thread.html/rc400db37710ee79378b6c52de3640493ff538c2beb41cefdbbdf2ab8%40%3Ccommits.submarine.apache.org%3E
- https://lists.apache.org/thread.html/rc400db37710ee79378b6c52de3640493ff538c2beb41cefdbbdf2ab8@%3Ccommits.submarine.apache.org%3E
- https://lists.apache.org/thread.html/rca37935d661f4689cb4119f1b3b224413b22be161b678e6e6ce0c69b%40%3Ccommits.nifi.apache.org%3E
- https://lists.apache.org/thread.html/rca37935d661f4689cb4119f1b3b224413b22be161b678e6e6ce0c69b@%3Ccommits.nifi.apache.org%3E
