# [M] Deserialization of Untrusted Data vulnerability in Apache Lucene Replicator.

## Summary
Severity: Medium
Advisory: GHSA-g643-xq6w-r67c
CVE: CVE-2024-45772
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:A/AC:H/PR:H/UI:N/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2024-09-30
Source: https://github.com/advisories/GHSA-g643-xq6w-r67c
Type: github-advisory

## Affected
- Maven: `org.apache.lucene:lucene-replicator` — affected >=4.4.0 <9.12.0

## Details
This issue affects Apache Lucene's replicator module: from 4.4.0 before 9.12.0.
The deprecated org.apache.lucene.replicator.http package is affected.
The org.apache.lucene.replicator.nrt package is not affected.

Users are recommended to upgrade to version 9.12.0, which fixes the issue.

The deserialization can only be triggered if users actively deploy an network-accessible implementation and a corresponding client using a HTTP library that uses the API (e.g., a custom servlet and HTTPClient). Java serialization filters (such as -Djdk.serialFilter='!*' on the commandline) can mitigate the issue on vulnerable versions without impacting functionality.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-45772
- https://gitbox.apache.org/repos/asf?p=lucene.git
- https://lists.apache.org/thread/3f3oph7bqnqspb9q5p0gm5mgc1b6thjo
- http://www.openwall.com/lists/oss-security/2024/09/29/1
