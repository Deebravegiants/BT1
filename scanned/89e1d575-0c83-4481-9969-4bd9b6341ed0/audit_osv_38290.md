# [H] CVE-2026-37235

## Summary
Severity: High
Advisory: CVE-2026-37235
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-01
Source: https://osv.dev/vulnerability/CVE-2026-37235
Type: osv

## Details
FlexRIC v2.0.0 trusts the xapp_id field from E42 message payloads without binding it to the sender's SCTP association. The validation function valid_xapp_id() only checks that the value is within the assigned range. A remote unauthenticated attacker can impersonate any xApp by specifying their xapp_id in requests sent to the iApp (port 36422), causing responses to be misrouted to the victim xApp. This can crash the victim xApp, the RIC, or the iApp itself through state inconsistencies in the red-black tree data structure.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/37xxx/CVE-2026-37235.json
- https://github.com/MinamiKotor1/oran-security-advisories-zhongnan-luo/blob/main/advisories/CVE-2026-37235.md
- https://nvd.nist.gov/vuln/detail/CVE-2026-37235
- https://gitlab.eurecom.fr/mosaic5g/flexric
