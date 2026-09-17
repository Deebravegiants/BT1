# [C] Apache James server: Privilege escalation via JMX pre-authentication deserialization

## Summary
Severity: Critical
Advisory: GHSA-px7w-c9gw-7gj3
CVE: CVE-2023-51518
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-02-27
Source: https://github.com/advisories/GHSA-px7w-c9gw-7gj3
Type: github-advisory

## Affected
- Maven: `org.apache.james:james-server` — affected >=0 <3.7.5
- Maven: `org.apache.james:james-server` — affected >=3.8.0 <3.8.1

## Details
Apache James prior to version 3.7.5 and 3.8.0 exposes a JMX endpoint on localhost subject to pre-authentication deserialisation of untrusted data.
Given a deserialisation gadjet, this could be leveraged as part of an exploit chain that could result in privilege escalation.
Note that by default JMX endpoint is only bound locally.

We recommend users to:
 - Upgrade to a non-vulnerable Apache James version

 - Run Apache James isolated from other processes (docker - dedicated virtual machine)
 - If possible turn off JMX

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-51518
- https://lists.apache.org/thread/wbdm61ch6l0kzjn6nnfmyqlng82qz0or
