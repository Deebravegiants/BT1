# [H] Apache Camel-Lucene: The query control headers used non-Camel-prefixed names (QUERY, RETURN_LUCENE_DOCS) that bypass the HTTP header filter, allowing an HTTP client to inject the full-text search query

## Summary
Severity: High
Advisory: GHSA-566h-v38h-3xp3
CVE: CVE-2026-46585
CWE: CWE-20, CWE-639
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-06
Source: https://github.com/advisories/GHSA-566h-v38h-3xp3
Type: github-advisory

## Affected
- Maven: `org.apache.camel:camel-lucene` — affected >=4.0.0 <4.14.8
- Maven: `org.apache.camel:camel-lucene` — affected >=4.15.0 <4.18.3
- Maven: `org.apache.camel:camel-lucene` — affected >=4.19.0 <4.21.0

## Details
Improper Input Validation, Authorization Bypass Through User-Controlled Key vulnerability in Apache Camel Lucene Component.

The camel-lucene producer reads the search phrase from an Exchange header (LuceneConstants.HEADER_QUERY) whose value was the plain string QUERY (and RETURN_LUCENE_DOCS for HEADER_RETURN_LUCENE_DOCS). Because these names do not start with the Camel / camel prefix, HttpHeaderFilterStrategy - which blocks only the Camel header namespace on the HTTP boundary - let them pass from an inbound HTTP request straight into the Exchange. In a route that exposes a Lucene query operation behind an HTTP consumer (for example platform-http), any HTTP client could therefore set the QUERY header and have its value executed against the full-text index, overriding the query the route intended to run. Depending on what is indexed, this allows reading documents the request should not have access to (for example a match-all query returns the entire index, or the route's intended per-user filter can be replaced), and expensive regular-expression queries can consume significant CPU. No credentials are required when the HTTP consumer is unauthenticated.
This issue affects Apache Camel: from 4.0.0 before 4.14.8, from 4.15.0 before 4.18.3, from 4.19.0 before 4.21.0.

Users are recommended to upgrade to version 4.21.0, which fixes the issue. If users are on the 4.14.x LTS releases stream, then they are suggested to upgrade to 4.14.8. If users are on the 4.18.x releases stream, then they are suggested to upgrade to 4.18.3. After upgrading, routes that set the query via the raw header name must use CamelLuceneQuery (and CamelLuceneReturnLuceneDocs) instead of QUERY / RETURN_LUCENE_DOCS. For deployments that cannot upgrade immediately, strip the attacker-controllable headers before the Lucene producer and set the query from a trusted source (for example removeHeader('QUERY') and removeHeader('RETURN_LUCENE_DOCS'), then setHeader('QUERY', constant(...)) at the start of the route).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-46585
- https://github.com/apache/camel/pull/23208
- https://github.com/apache/camel/pull/23220
- https://github.com/apache/camel/pull/23232
- https://github.com/apache/camel/commit/16a70d48145605c1a35e909d308bf9e5e2d3e7d8
- https://github.com/apache/camel/commit/349f197115d60e0c180cf9836e08f4aeb5a87872
- https://github.com/apache/camel/commit/878ea07996caff19ed227984bf6cb6cf01983422
- https://camel.apache.org/security/CVE-2026-46585.html
- https://github.com/apache/camel
- https://github.com/apache/camel/releases/tag/camel-4.14.8
- https://github.com/apache/camel/releases/tag/camel-4.18.3
- https://github.com/apache/camel/releases/tag/camel-4.21.0
- https://issues.apache.org/jira/browse/CAMEL-23509
- http://www.openwall.com/lists/oss-security/2026/07/05/12
