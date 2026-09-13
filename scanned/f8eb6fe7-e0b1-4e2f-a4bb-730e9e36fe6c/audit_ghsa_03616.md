# [H] Apache NiFi user log out issue

## Summary
Severity: High
Advisory: GHSA-fmqw-vqh5-cwq9
CVE: CVE-2019-12421
CWE: CWE-613
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-12-02
Source: https://github.com/advisories/GHSA-fmqw-vqh5-cwq9
Type: github-advisory

## Affected
- Maven: `org.apache.nifi:nifi-web-security` — affected >=1.3.0 <1.10.0
- Maven: `org.apache.nifi:nifi-web-api` — affected >=1.3.0 <1.10.0

## Details
When using an authentication mechanism other than PKI, when the user clicks Log Out in NiFi versions 1.0.0 to 1.9.2, NiFi invalidates the authentication token on the client side but not on the server side. This permits the user's client-side token to be used for up to 12 hours after logging out to make API requests to NiFi.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-12421
- https://github.com/apache/nifi/pull/3362
- https://github.com/apache/nifi/commit/cf6f5172503ce438c6c22c334c9367f774db7b24
- https://lists.apache.org/thread.html/rca37935d661f4689cb4119f1b3b224413b22be161b678e6e6ce0c69b@%3Ccommits.nifi.apache.org%3E
- https://nifi.apache.org/security.html#CVE-2019-12421
