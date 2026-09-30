# [C] PX4 Autopilot Missing authentication for critical function

## Summary
Severity: Critical
Advisory: CVE-2026-1579
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-03-31
Source: https://osv.dev/vulnerability/CVE-2026-1579
Type: osv

## Details
The MAVLink communication protocol does not require cryptographic 
authentication by default. When MAVLink 2.0 message signing is not 
enabled, any message -- including SERIAL_CONTROL, which provides 
interactive shell access -- can be sent by an unauthenticated party with
 access to the MAVLink interface. PX4 provides MAVLink 2.0 message 
signing as the cryptographic authentication mechanism for all MAVLink 
communication. When signing is enabled, unsigned messages are rejected 
at the protocol level.

## References
- https://docs.px4.io/main/en/mavlink/message_signing
- https://docs.px4.io/main/en/mavlink/security_hardening
- https://github.com/cisagov/CSAF/blob/develop/csaf_files/OT/white/2026/icsa-26-090-02.json
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/1xxx/CVE-2026-1579.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-1579
- https://www.cisa.gov/news-events/ics-advisories/icsa-26-090-02
