# [M] Apache NiFi process group information disclosure

## Summary
Severity: Medium
Advisory: GHSA-26p8-xrj2-mv53
CVE: CVE-2019-10083
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2019-12-02
Source: https://github.com/advisories/GHSA-26p8-xrj2-mv53
Type: github-advisory

## Affected
- Maven: `org.apache.nifi:nifi-web-api` — affected >=1.3.0 <1.10.0
- Maven: `org.apache.nifi:nifi` — affected >=1.3.0 <1.10.0

## Details
When updating a Process Group via the API in NiFi versions 1.3.0 to 1.9.2, the response to the request includes all of its contents (at the top most level, not recursively). The response included details about processors and controller services which the user may not have had read access to.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10083
- https://lists.apache.org/thread.html/rca37935d661f4689cb4119f1b3b224413b22be161b678e6e6ce0c69b@%3Ccommits.nifi.apache.org%3E
- https://nifi.apache.org/security.html#CVE-2019-10083
