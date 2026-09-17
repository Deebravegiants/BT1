# [H] Memory leak

## Summary
Severity: High
Advisory: CVE-2024-8376
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:L/VA:H/SC:N/SI:N/SA:N)
Published: 2024-10-11
Source: https://osv.dev/vulnerability/CVE-2024-8376
Type: osv

## Details
In Eclipse Mosquitto up to version 2.0.18a, an attacker can achieve memory leaking, segmentation fault or heap-use-after-free by sending specific sequences of "CONNECT", "DISCONNECT", "SUBSCRIBE", "UNSUBSCRIBE" and "PUBLISH" packets.

## References
- https://mosquitto.org/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/8xxx/CVE-2024-8376.json
- https://gitlab.eclipse.org/security/cve-assignement/-/issues/26
- https://nvd.nist.gov/vuln/detail/CVE-2024-8376
- https://gitlab.eclipse.org/security/vulnerability-reports/-/issues/216
- https://gitlab.eclipse.org/security/vulnerability-reports/-/issues/217
- https://gitlab.eclipse.org/security/vulnerability-reports/-/issues/218
- https://gitlab.eclipse.org/security/vulnerability-reports/-/issues/227
- https://github.com/eclipse-mosquitto/mosquitto/commit/1914b3ee2a18102d0a94cbdbbfeae1afa03edd17
- https://github.com/eclipse/mosquitto/releases/tag/v2.0.19
- https://github.com/eclipse/mosquitto
