# [M] SoftEther VPN with L2TP - 2.75x Amplification

## Summary
Severity: Medium
Advisory: CVE-2024-38520
Aliases: GHSA-j35p-p8pj-vqxq
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2024-06-26
Source: https://osv.dev/vulnerability/CVE-2024-38520
Type: osv

## Details
SoftEtherVPN is a an open-source cross-platform multi-protocol VPN Program. When SoftEtherVPN is deployed with L2TP enabled on a device, it introduces the possibility of the host being used for amplification/reflection traffic generation because it will respond to every packet with two response packets that are larger than the request packet size. These sorts of techniques are used by external actors who generate spoofed source IPs to target a destination on the internet. This vulnerability has been patched in version 5.02.5185.

## References
- https://github.com/SoftEtherVPN/SoftEtherVPN/releases/tag/5.02.5185
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38520.json
- https://github.com/SoftEtherVPN/SoftEtherVPN/security/advisories/GHSA-j35p-p8pj-vqxq
- https://nvd.nist.gov/vuln/detail/CVE-2024-38520
- https://github.com/SoftEtherVPN/SoftEtherVPN/commit/c2a7aa548137dc80c6aafdc645cf4dc34e0dc764
