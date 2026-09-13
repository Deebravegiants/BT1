# [H] Apache Kylin has Insufficiently Protected Credentials

## Summary
Severity: High
Advisory: GHSA-3vvc-v8c2-43r7
CVE: CVE-2023-29055
CWE: CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-01-29
Source: https://github.com/advisories/GHSA-3vvc-v8c2-43r7
Type: github-advisory

## Affected
- Maven: `org.apache.kylin:kylin-core-common` — affected >=2.0.0 <4.0.4

## Details
In Apache Kylin version 2.0.0 to 4.0.3, there is a Server Config web interface that displays the content of file 'kylin.properties', that may contain serverside credentials. When the kylin service runs over HTTP (or other plain text protocol), it is possible for network sniffers to hijack the HTTP payload and get access to the content of kylin.properties and potentially the containing credentials.

To avoid this threat, users are recommended to 

  *  Always turn on HTTPS so that network payload is encrypted.

  *  Avoid putting credentials in kylin.properties, or at least not in plain text.
  *  Use network firewalls to protect the serverside such that it is not accessible to external attackers.

  *  Upgrade to version Apache Kylin 4.0.4, which filters out the sensitive content that goes to the Server Config web interface.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-29055
- https://github.com/apache/kylin/commit/b60d5ae694dffc2281bfe0ef464eada0b3a9b774
- https://github.com/apache/kylin
- https://lists.apache.org/thread/o1bvyv9wnfkx7dxpfjlor20nykgsoh6r
- http://www.openwall.com/lists/oss-security/2024/01/29/1
