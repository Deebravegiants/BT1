# [C] Gradient: Unauthenticated worker on /proto → arbitrary NAR write / cache poisoning

## Summary
Severity: Critical
Advisory: CVE-2026-44592
Aliases: GHSA-49w6-gf3p-96m2
CVSS: 9.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:H)
Published: 2026-05-14
Source: https://osv.dev/vulnerability/CVE-2026-44592
Type: osv

## Details
Gradient is a nix-based continuous integration system. In 1.1.0, when GRADIENT_DISCOVERABLE=true (the default, and the NixOS module default), anyone who can reach /proto can register as a worker without any credentials by sending a fresh, never-registered worker UUID. The resulting session has PeerAuth::Open, i.e. it sees jobs from every organisation, and can immediately NarPush/NarUploaded arbitrary store paths into nar_storage and the cached_path table. This vulnerability is fixed in 1.1.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44592.json
- https://github.com/wavelens/gradient/security/advisories/GHSA-49w6-gf3p-96m2
- https://nvd.nist.gov/vuln/detail/CVE-2026-44592
