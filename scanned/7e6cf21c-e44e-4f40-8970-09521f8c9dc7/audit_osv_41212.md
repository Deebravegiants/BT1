# [M] Klever-Go: PubKeysBitmap padding bits bypass the BLS signature quorum

## Summary
Severity: Medium
Advisory: CVE-2026-58262
Aliases: GHSA-f9h7-4mmq-vgcq
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/CVE-2026-58262
Type: osv

## Details
Klever-Go is the Go implementation of the Klever blockchain protocol. Prior to 1.7.20, header signature verification counts the unused padding bits of the PubKeysBitmap toward the two-thirds validator quorum. These padding bits do not correspond to any validator and are ignored by the actual BLS aggregate-signature check, so a malicious or compromised block producer can set them to reach the required quorum while gathering fewer genuine validator signatures than the protocol demands. As a result, nodes that import or intercept the header accept it as correctly signed without a real two-thirds quorum, weakening consensus safety and undermining finality. This issue is fixed in version 1.7.20.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58262.json
- https://github.com/klever-io/klever-go/security/advisories/GHSA-f9h7-4mmq-vgcq
- https://nvd.nist.gov/vuln/detail/CVE-2026-58262
- https://github.com/klever-io/klever-go/commit/a11cb28e495e608d8034dbe83a91e89d0c68e0f7
