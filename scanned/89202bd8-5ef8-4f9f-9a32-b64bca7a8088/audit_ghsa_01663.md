# [H] Improper Input Validation in Apache Solr

## Summary
Severity: High
Advisory: GHSA-ww97-9w65-2crx
CVE: CVE-2019-17558
CWE: CWE-20, CWE-74, CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H/E:H (CVSS_V3)
Published: 2020-02-12
Source: https://github.com/advisories/GHSA-ww97-9w65-2crx
Type: github-advisory

## Affected
- Maven: `org.apache.solr:solr-core` — affected >=5.0.0 <8.4.0
- Maven: `org.apache.solr:solr-core` — affected >=6.0.0 <8.4.0
- Maven: `org.apache.solr:solr-core` — affected >=7.0.0 <8.4.0
- Maven: `org.apache.solr:solr-core` — affected >=8.0.0 <8.4.0

## Details
Apache Solr 5.0.0 to Apache Solr 8.3.1 are vulnerable to a Remote Code Execution through the VelocityResponseWriter. A Velocity template can be provided through Velocity templates in a configset `velocity/` directory or as a parameter. A user defined configset could contain renderable, potentially malicious, templates. Parameter provided templates are disabled by default, but can be enabled by setting `params.resource.loader.enabled` by defining a response writer with that setting set to `true`. Defining a response writer requires configuration API access. Solr 8.4 removed the params resource loader entirely, and only enables the configset-provided template rendering when the configset is `trusted` (has been uploaded by an authenticated user).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-17558
- https://github.com/apache/lucene-solr/pull/1156
- https://lists.apache.org/thread.html/r7f21ab40a9b17b1a703db84ac56773fcabacd4cc1eb5c4700d17c071%40%3Cissues.lucene.apache.org%3E
- https://lists.apache.org/thread.html/r7f21ab40a9b17b1a703db84ac56773fcabacd4cc1eb5c4700d17c071@%3Cissues.lucene.apache.org%3E
- https://lists.apache.org/thread.html/r8a36e4f92f4449dec517e560e1b55639f31b3aca26c37bbad45e31de%40%3Cissues.lucene.apache.org%3E
- https://lists.apache.org/thread.html/r8a36e4f92f4449dec517e560e1b55639f31b3aca26c37bbad45e31de@%3Cissues.lucene.apache.org%3E
- https://lists.apache.org/thread.html/r8e7a3c253a695a7667da0b0ec57f9bb0e31f039e62afbc00a1d96f7b%40%3Csolr-user.lucene.apache.org%3E
- https://lists.apache.org/thread.html/r8e7a3c253a695a7667da0b0ec57f9bb0e31f039e62afbc00a1d96f7b@%3Csolr-user.lucene.apache.org%3E
- https://lists.apache.org/thread.html/r9271d030452170ba6160c022757e1b5af8a4c9ccf9e04164dec02e7f%40%3Cissues.lucene.apache.org%3E
- https://lists.apache.org/thread.html/r9271d030452170ba6160c022757e1b5af8a4c9ccf9e04164dec02e7f@%3Cissues.lucene.apache.org%3E
- https://lists.apache.org/thread.html/r99c3f7ec3a079e2abbd540ecdb55a0e2a0f349ca7084273a12e87aeb%40%3Cissues.lucene.apache.org%3E
- https://lists.apache.org/thread.html/r99c3f7ec3a079e2abbd540ecdb55a0e2a0f349ca7084273a12e87aeb@%3Cissues.lucene.apache.org%3E
- https://lists.apache.org/thread.html/ra29fa6ede5184385bf2c63e8ec054990a7d4622bba1d244bee70d82d%40%3Cissues.lucene.apache.org%3E
- https://lists.apache.org/thread.html/ra29fa6ede5184385bf2c63e8ec054990a7d4622bba1d244bee70d82d@%3Cissues.lucene.apache.org%3E
- https://lists.apache.org/thread.html/rafc939fdd753f55707841cd5886fc7fcad4d8d8ba0c72429b3220a9a%40%3Cissues.lucene.apache.org%3E
- https://lists.apache.org/thread.html/rafc939fdd753f55707841cd5886fc7fcad4d8d8ba0c72429b3220a9a@%3Cissues.lucene.apache.org%3E
- https://lists.apache.org/thread.html/rb964fe5c4e3fc05f75e8f74bf6b885f456b7a7750c36e9a8045c627a%40%3Cissues.lucene.apache.org%3E
- https://lists.apache.org/thread.html/rb964fe5c4e3fc05f75e8f74bf6b885f456b7a7750c36e9a8045c627a@%3Cissues.lucene.apache.org%3E
- https://lists.apache.org/thread.html/rc400db37710ee79378b6c52de3640493ff538c2beb41cefdbbdf2ab8%40%3Ccommits.submarine.apache.org%3E
- https://lists.apache.org/thread.html/rc400db37710ee79378b6c52de3640493ff538c2beb41cefdbbdf2ab8@%3Ccommits.submarine.apache.org%3E
