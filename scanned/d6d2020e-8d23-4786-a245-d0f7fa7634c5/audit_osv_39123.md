# [C] Tautulli vulnerable to unauthenticated SSRF in /image/<hash> via attacker-seeded image hash replay

## Summary
Severity: Critical
Advisory: CVE-2026-43986
Aliases: GHSA-m6j6-rc2c-8vpm
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L)
Published: 2026-06-04
Source: https://osv.dev/vulnerability/CVE-2026-43986
Type: osv

## Details
Tautulli is a Python based monitoring and tracking tool for Plex Media Server. Versions prior to 2.17.1 expose a public `/image/<hash>` route that resolves attacker-controlled entries from `image_hash_lookup` and replays them through the same server-side image fetch logic used by authenticated image proxying. A low-privilege guest user can seed a malicious external image URL into this lookup table and then trigger server-side fetches through a fully unauthenticated endpoint. This turns an authenticated SSRF primitive into a persistent unauthenticated SSRF gadget. Once the malicious hash entry exists, any external user can request `/image/<hash>.png` and cause the PMS or Tautulli host to fetch an arbitrary attacker-chosen URL. Version 2.17.1 patches the issue.

## References
- https://github.com/Tautulli/Tautulli/releases/tag/v2.17.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43986.json
- https://github.com/Tautulli/Tautulli/security/advisories/GHSA-m6j6-rc2c-8vpm
- https://nvd.nist.gov/vuln/detail/CVE-2026-43986
