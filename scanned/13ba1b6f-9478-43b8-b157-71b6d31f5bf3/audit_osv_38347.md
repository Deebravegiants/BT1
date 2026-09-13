# [H] Pre-Auth EAP-TLS DoS on SoftEther VPN Developer Edition

## Summary
Severity: High
Advisory: CVE-2026-39312
Aliases: GHSA-q5g3-qhc6-pr3h
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/CVE-2026-39312
Type: osv

## Details
SoftEtherVPN is a an open-source cross-platform multi-protocol VPN Program. In 5.2.5188 and earlier, a pre-authentication denial-of-service vulnerability exists in SoftEther VPN Developer Edition 5.2.5188 (and likely earlier versions of Developer Edition). An unauthenticated remote attacker can crash the vpnserver process by sending a single malformed EAP-TLS packet over raw L2TP (UDP/1701), terminating all active VPN sessions.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39312.json
- https://github.com/SoftEtherVPN/SoftEtherVPN/security/advisories/GHSA-q5g3-qhc6-pr3h
- https://nvd.nist.gov/vuln/detail/CVE-2026-39312
