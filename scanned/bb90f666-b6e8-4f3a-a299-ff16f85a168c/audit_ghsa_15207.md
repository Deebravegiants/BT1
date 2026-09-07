# [M] Apache Solr allows read access to host environmet variables

## Summary
Severity: Medium
Advisory: GHSA-gg7w-pw2r-x2cq
CVE: CVE-2023-50290
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-01-15
Source: https://github.com/advisories/GHSA-gg7w-pw2r-x2cq
Type: github-advisory

## Affected
- Maven: `org.apache.solr:solr-core` — affected >=9.0.0 <9.3.0

## Details
Exposure of Sensitive Information to an Unauthorized Actor vulnerability in Apache Solr.

The Solr Metrics API publishes all unprotected environment variables available to each Apache Solr instance. Users are able to specify which environment variables to hide, however, the default list is designed to work for known secret Java system properties. Environment variables cannot be strictly defined in Solr, like Java system properties can be, and may be set for the entire host, unlike Java system properties which are set per-Java-proccess.

The Solr Metrics API is protected by the "metrics-read" permission. Therefore, Solr Clouds with Authorization setup will only be vulnerable via users with the "metrics-read" permission.

This issue affects Apache Solr: from 9.0.0 before 9.3.0.

Users are recommended to upgrade to version 9.3.0 or later, in which environment variables are not published via the Metrics API.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-50290
- https://github.com/apache/solr/commit/35fc4bdc48171d9a64251c54a1e76deb558cf9d8
- https://github.com/apache/lucene-solr
- https://issues.apache.org/jira/browse/SOLR-16808
- https://solr.apache.org/security.html#cve-2023-50290-apache-solr-allows-read-access-to-host-environment-variables
