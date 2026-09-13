# [M] barebox Out-of-Bounds Read in DHCP Option Parsing

## Summary
Severity: Medium
Advisory: CVE-2026-34960
CVSS: 6.0 (CVSS:4.0/AV:A/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-11
Source: https://osv.dev/vulnerability/CVE-2026-34960
Type: osv

## Details
barebox prior to version 2026.04.0 contains an out-of-bounds read vulnerability in DHCP option parsing within the dhcp_message_type() function that fails to verify the options pointer remains within received packet bounds. An attacker on the same broadcast domain can send a crafted DHCP Offer or ACK packet without a proper 0xff end marker to cause the parser to read past valid packet data and potentially crash the system.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34960.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-34960
- https://www.vulncheck.com/advisories/barebox-out-of-bounds-read-in-dhcp-option-parsing
- https://github.com/barebox/barebox/releases/tag/v2026.04.0
- https://github.com/barebox/barebox
- https://y637f9qq2x.com/posts/barebox-sandbox-vulns/
