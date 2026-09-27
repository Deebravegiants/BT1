# [H] Sonic 3 A.I.R. Missing Source Address Validation in ConnectionManager

## Summary
Severity: High
Advisory: CVE-2026-66732
CVSS: 7.5 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2026-66732
Type: osv

## Details
Sonic 3 A.I.R. before commit 2492d18 contains a missing source address validation vulnerability in ConnectionManager where established connections are resolved by a two-byte local connection handle alone without verifying that the datagram source address matches the registered remote address for the connection. An on-path attacker who can observe cleartext UDP traffic can inject arbitrary packets into any established session by forging the two-byte connection identifier, enabling session termination via TerminateConnectionPacket, arbitrary channel message forgery, and forged request responses without requiring IP address spoofing.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/66xxx/CVE-2026-66732.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-66732
- https://www.vulncheck.com/advisories/sonic-3-a-i-r-missing-source-address-validation-in-connectionmanager
- https://github.com/Eukaryot/sonic3air/commit/2492d1882cd2cf1cc1d7415729ce5c4fd686cd4f
- https://github.com/Eukaryot/sonic3air
