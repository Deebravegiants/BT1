# [M] OpenSIPS: Denial of Service in SDP bandwidth parsing via QoS SDP cloning

## Summary
Severity: Medium
Advisory: CVE-2026-46334
Aliases: GHSA-rh36-mhpv-cx2r
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-04
Source: https://osv.dev/vulnerability/CVE-2026-46334
Type: osv

## Details
OpenSIPS is a Session Initiation Protocol (SIP) server implementation. Versions prior to 3.6.6 and 4.0.0-rc1 contain a denial of service vulnerability in the SDP bandwidth-line parsing logic. A SIP request with Content-Type: application/sdp and a malformed session-level SDP bandwidth line missing the required colon delimiter can corrupt parsed SDP bandwidth metadata. When a route or module subsequently clones the corrupted SDP state, as occurs with dialog and QoS processing, the OpenSIPS worker process crashes. An unauthenticated remote attacker can therefore trigger a crash in any configuration whose routing script parses attacker-controlled SDP and applies dialog/QoS processing. This issue has been fixed in versions 3.6.6 and 4.0.0-rc1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46334.json
- https://github.com/OpenSIPS/opensips/security/advisories/GHSA-rh36-mhpv-cx2r
- https://nvd.nist.gov/vuln/detail/CVE-2026-46334
- https://github.com/OpenSIPS/opensips/commit/8fe74b01f6fbf86c0b5e290735275530cb65e0fb
- https://github.com/OpenSIPS/opensips/commit/ac5309d5b8206cd3dbe1b4e01567c8db1ce31444
