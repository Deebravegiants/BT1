# [H] DevGuard has improper authorization on public assets

## Summary
Severity: High
Advisory: GHSA-6p54-fw2f-q7gf
CVE: CVE-2026-48089
CWE: CWE-285, CWE-863
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:N/VI:H/VA:H/SC:N/SI:H/SA:N (CVSS_V4)
Published: 2026-06-11
Source: https://github.com/advisories/GHSA-6p54-fw2f-q7gf
Type: github-advisory

## Affected
- Go: `github.com/l3montree-dev/devguard` — affected >=0 <1.4.2

## Details
### Impact

On a DevGuard API instance with one or more **public assets**, any authenticated user — including users from a different organization with no membership or role in the affected org/project — can create, update, reapply, and delete **VEX rules** on those public assets. The same flaw affects the other vulnerability-triage write endpoints exposed under a public asset, including:

- VEX rule create / update / reapply / delete
- Dependency-vuln event creation (accept / reject / mitigate decisions), batch event creation, vuln sync, and mitigation
- License risk creation
- External reference writes
- Artifact creation and license refresh

The attacker needs a valid account on the instance, but no membership in the victim organization, project, or asset is required.

**Security impact** is primarily to **integrity** of the vulnerability picture of public assets: an attacker can mark CVEs as false-positive, silence vulnerabilities, attach misleading justifications, or delete legitimate triage rules — undermining the trustworthiness of every consumer of the affected asset's VEX/SBOM output. Because public assets are by definition consumed by third parties (downstream users, supply-chain consumers, the published vex.json/sbom.json), the blast radius extends to anyone relying on that data.

Private assets are **not affected** by this advisory: the public-read exemption that enables the bypass does not apply to them, and access remains correctly gated by organization/project membership. The private setting is only relevant in DevGuard itself —  there is no impact given when you have an open-source project on e.g. GitLab/GitHub and a private DevGuard asset connected.

### Patches

Version `v1.4.2`contains a patch. Users should upgrade to the patched release as soon as it is available.

### Workarounds

If developers cannot upgrade their applications immediately:

- ** They should make affected assets non-public.** In the asset settings, switch visibility from public to private. This removes the public-read exemption in the access-control middleware and restores correct authorization on all write endpoints for that asset. Downstream consumers that previously relied on the public `vex.json` / `sbom.json` endpoints will need to be granted explicit access or must receive an exported file version until the patched release is deployed.

### Resources
Fixed commit: https://github.com/l3montree-dev/devguard/commit/1be88ec1309a5dc0566e35a23bdc4ea3ecd11417

### Credit

DeevGuard thanks @philipflohr ([awesome-it.de](https://awesome-it.de/)) for finding and responsibly reporting this vulnerability!

## References
- https://github.com/l3montree-dev/devguard/security/advisories/GHSA-6p54-fw2f-q7gf
- https://nvd.nist.gov/vuln/detail/CVE-2026-48089
- https://github.com/l3montree-dev/devguard/commit/1be88ec1309a5dc0566e35a23bdc4ea3ecd11417
- https://github.com/l3montree-dev/devguard
