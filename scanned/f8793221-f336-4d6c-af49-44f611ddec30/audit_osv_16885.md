# [C] CVE-2020-10283

## Summary
Severity: Critical
Advisory: CVE-2020-10283
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-08-20
Source: https://osv.dev/vulnerability/CVE-2020-10283
Type: osv

## Details
The Micro Air Vehicle Link (MAVLink) protocol presents authentication mechanisms on its version 2.0 however according to its documentation, in order to maintain backwards compatibility, GCS and autopilot negotiate the version via the AUTOPILOT_VERSION message. Since this negotiation depends on the answer, an attacker may craft packages in a way that hints the autopilot to adopt version 1.0 of MAVLink for the communication. Given the lack of authentication capabilities in such version of MAVLink (refer to CVE-2020-10282), attackers may use this method to bypass authentication capabilities and interact with the autopilot directly.

## References
- https://github.com/aliasrobotics/RVD/issues/3316
