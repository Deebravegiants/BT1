# [M] Cache confusion in Jenkins Eiffel Broadcaster Plugin 

## Summary
Severity: Medium
Advisory: GHSA-fpw7-8gjc-jwqj
CVE: CVE-2025-24400
CWE: CWE-276, CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2025-01-22
Source: https://github.com/advisories/GHSA-fpw7-8gjc-jwqj
Type: github-advisory

## Affected
- Maven: `com.axis.jenkins.plugins.eiffel:eiffel-broadcaster` — affected >=2.8.0 <2.10.3

## Details
The Jenkins Eiffel Broadcaster Plugin allows events published to RabbitMQ to be signed using certificate credentials. To improve performance, the plugin caches some data from the credential.

Eiffel Broadcaster Plugin 2.8.0 through 2.10.2 (both inclusive) uses the credential ID as the cache key. This allows attackers able to create a credential with the same ID as a legitimate one in a different credentials store, to sign an event published to RabbitMQ with the legitimate certificate credentials.

Eiffel Broadcaster Plugin 2.10.3 removes the cache.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-24400
- https://github.com/jenkinsci/eiffel-broadcaster-plugin
- https://www.jenkins.io/security/advisory/2025-01-22/#SECURITY-3485
