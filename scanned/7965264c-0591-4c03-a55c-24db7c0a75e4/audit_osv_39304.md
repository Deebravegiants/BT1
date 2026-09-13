# [C] OpenSIPS: Buffer Overflow in Base64 Encode Transformation

## Summary
Severity: Critical
Advisory: CVE-2026-45100
Aliases: GHSA-35fr-6rv9-vp68
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-08-04
Source: https://osv.dev/vulnerability/CVE-2026-45100
Type: osv

## Details
OpenSIPS is a Session Initiation Protocol (SIP) server implementation. Versions 3.4.0-beta through 3.6.5 and 4.0.0-beta contain a buffer overflow in the {s.b64encode} string transformation. The size check for {s.b64encode} only verifies that the input fits within the 64 KB transformation buffer, but base64 encoding expands the data by roughly a third, so an input between about 49,153 and 65,535 bytes produces more output than the buffer can hold and overflows it by up to 21,844 bytes. Because these transformation buffers sit next to each other in memory and are reused for chained transformations, the overflow writes attacker-controlled data into the adjacent buffer and corrupts values used by later transformations processing the same SIP message. A remote attacker can trigger this by sending a SIP message with a large header value (roughly 50,000 bytes or more) when the routing script applies  {s.b64encode}  to attacker-controlled input, making exploitability dependent on the deployment's routing configuration. This issue has been fixed in versions 3.6.6 and 4.0.0-rc1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45100.json
- https://github.com/OpenSIPS/opensips/security/advisories/GHSA-35fr-6rv9-vp68
- https://nvd.nist.gov/vuln/detail/CVE-2026-45100
- https://github.com/OpenSIPS/opensips/commit/4d23613b65579b073784a07a65d3bf52443a4efb
- https://github.com/OpenSIPS/opensips/commit/5f103effaf5f372cccffe0b138f16998eba12668
