# [H] Code injection in Apache NiFi and NiFi Registry

## Summary
Severity: High
Advisory: GHSA-77hf-23pq-2g7c
CVE: CVE-2022-33140
CWE: CWE-74, CWE-78
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-06-16
Source: https://github.com/advisories/GHSA-77hf-23pq-2g7c
Type: github-advisory

## Affected
- Maven: `org.apache.nifi.registry:nifi-registry-core` — affected >=0.6.0 <1.16.3
- Maven: `org.apache.nifi:nifi` — affected >=1.10.0 <1.16.3

## Details
The optional ShellUserGroupProvider in Apache NiFi 1.10.0 to 1.16.2 and Apache NiFi Registry 0.6.0 to 1.16.2 does not neutralize arguments for group resolution commands, allowing injection of operating system commands on Linux and macOS platforms. The ShellUserGroupProvider is not included in the default configuration. Command injection requires ShellUserGroupProvider to be one of the enabled User Group Providers in the Authorizers configuration. Command injection also requires an authenticated user with elevated privileges. Apache NiFi requires an authenticated user with authorization to modify access policies in order to execute the command. Apache NiFi Registry requires an authenticated user with authorization to read user groups in order to execute the command. The resolution removes command formatting based on user-provided arguments.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-33140
- https://github.com/apache/nifi
- https://lists.apache.org/thread/bzs2pcdjsdrh5039oslmfr9mbs9qqdhr
- https://nifi.apache.org/security.html#CVE-2022-33140
