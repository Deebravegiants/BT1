# [H] Inadequate Encryption Strength in Apache NiFi

## Summary
Severity: High
Advisory: GHSA-rfmp-jvr7-hx78
CVE: CVE-2020-9491
CWE: CWE-327
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-rfmp-jvr7-hx78
Type: github-advisory

## Affected
- Maven: `org.apache.nifi:nifi` — affected >=1.2.0 <1.12.0-RC1

## Details
In Apache NiFi 1.2.0 to 1.11.4, the NiFi UI and API were protected by mandating TLS v1.2, as well as listening connections established by processors like ListenHTTP, HandleHttpRequest, etc. However intracluster communication such as cluster request replication, Site-to-Site, and load balanced queues continued to support TLS v1.0 or v1.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-9491
- https://github.com/apache/nifi/commit/441781cec50f77d9f1e65093f55bbd614b8c5ec6
- https://github.com/apache/nifi
- https://lists.apache.org/thread.html/r2d9c21f9ec35d66f2bb42f8abe876dabd786166b6284e9a33582c718@%3Ccommits.nifi.apache.org%3E
- https://lists.apache.org/thread.html/re48582efe2ac973f8cff55c8b346825cb491c71935e15ab2d61ef3bf@%3Ccommits.nifi.apache.org%3E
- https://nifi.apache.org/security#CVE-2020-9491
