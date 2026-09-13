# [M] DoS from MQTT v5.0 Deserialization Fault in core MQTT

## Summary
Severity: Medium
Advisory: CVE-2026-8686
Aliases: GHSA-6qh9-r6jp-2wxc
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-15
Source: https://osv.dev/vulnerability/CVE-2026-8686
Type: osv

## Details
Missing bounds validation in the MQTT v5.0 property parser in coreMQTT before 5.0.1 allows an MQTT broker to cause a denial of service by sending a crafted packet.



To remediate this issue, users should upgrade to v5.0.1.

## References
- https://aws.amazon.com/security/security-bulletins/2026-032-aws/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/8xxx/CVE-2026-8686.json
- https://github.com/FreeRTOS/coreMQTT/security/advisories/GHSA-6qh9-r6jp-2wxc
- https://nvd.nist.gov/vuln/detail/CVE-2026-8686
- https://github.com/FreeRTOS/coreMQTT/releases/tag/v5.0.1
