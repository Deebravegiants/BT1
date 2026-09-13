# [M] Outline: Unauthorized Document Publication via Mixed collectionId+documentId Share

## Summary
Severity: Medium
Advisory: CVE-2026-43889
Aliases: GHSA-rg4j-pmch-w6pm
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-05-11
Source: https://osv.dev/vulnerability/CVE-2026-43889
Type: osv

## Details
Outline is a service that allows for collaborative documentation. Prior to 1.7.0, the shares.create API accepts both collectionId and documentId simultaneously and, when published=false, only verifies read access for each—skipping the "share" permission check. A subsequent shares.update authorizes publication using an OR policy (can share collection OR can share document), so an attacker who holds share permission on one unrelated collection can publish a share that exposes an arbitrary document they cannot legitimately share, making it publicly accessible to unauthenticated users. This vulnerability is fixed in 1.7.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43889.json
- https://github.com/outline/outline/security/advisories/GHSA-rg4j-pmch-w6pm
- https://nvd.nist.gov/vuln/detail/CVE-2026-43889
