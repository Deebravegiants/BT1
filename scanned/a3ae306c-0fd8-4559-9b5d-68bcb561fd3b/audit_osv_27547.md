# [M] Consensys Discovery Nonce Reuse

## Summary
Severity: Medium
Advisory: CVE-2024-23688
Aliases: GHSA-w3hj-wr2q-x83g
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2024-01-19
Source: https://osv.dev/vulnerability/CVE-2024-23688
Type: osv

## Details
Consensys Discovery versions less than 0.4.5 uses the same AES/GCM nonce for the entire session. which should ideally be unique for every message. The node's private key isn't compromised, only the session key generated for specific peer communication is exposed.

## References
- https://repo.maven.apache.org/maven2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/23xxx/CVE-2024-23688.json
- https://github.com/ConsenSys/discovery/security/advisories/GHSA-w3hj-wr2q-x83g
- https://github.com/advisories/GHSA-w3hj-wr2q-x83g
- https://nvd.nist.gov/vuln/detail/CVE-2024-23688
- https://vulncheck.com/advisories/vc-advisory-GHSA-w3hj-wr2q-x83g
