# [H] Apache Solr can leak certain passwords due to System Property redaction logic inconsistencies

## Summary
Severity: High
Advisory: GHSA-3hwc-rqwp-v36q
CVE: CVE-2023-50291
CWE: CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-02-09
Source: https://github.com/advisories/GHSA-3hwc-rqwp-v36q
Type: github-advisory

## Affected
- Maven: `org.apache.solr:solr-core` — affected >=6.0.0 <8.11.3
- Maven: `org.apache.solr:solr-core` — affected >=9.0.0 <9.3.0

## Details
Insufficiently Protected Credentials vulnerability in Apache Solr.

This issue affects Apache Solr from 6.0.0 through 8.11.2, from 9.0.0 before 9.3.0.
One of the two endpoints that publishes the Solr process' Java system properties, /admin/info/properties, was only setup to hide system properties that had "password" contained in the name.
There are a number of sensitive system properties, such as "basicauth" and "aws.secretKey" do not contain "password", thus their values were published via the "/admin/info/properties" endpoint.
This endpoint populates the list of System Properties on the home screen of the Solr Admin page, making the exposed credentials visible in the UI.

This /admin/info/properties endpoint is protected under the "config-read" permission.
Therefore, Solr Clouds with Authorization enabled will only be vulnerable through logged-in users that have the "config-read" permission.
Users are recommended to upgrade to version 9.3.0 or 8.11.3, both of which fix the issue.
A single option now controls hiding Java system property for all endpoints, "-Dsolr.hiddenSysProps".
By default all known sensitive properties are hidden (including "-Dbasicauth"), as well as any property with a name containing "secret" or "password".

Users who cannot upgrade can also use the following Java system property to fix the issue:
  `-Dsolr.redaction.system.pattern=.*(password|secret|basicauth).*`

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-50291
- https://github.com/apache/solr/commit/659021c7d50164a3166887f24875228431b02102
- https://github.com/apache/solr/commit/98c198810f2cd934d23d0d80aadb570a2bbb3b8e
- https://github.com/apache/solr
- https://issues.apache.org/jira/browse/SOLR-16809
- https://solr.apache.org/security.html#cve-2023-50291-apache-solr-can-leak-certain-passwords-due-to-system-property-redaction-logic-inconsistencies
- http://www.openwall.com/lists/oss-security/2024/02/09/4
