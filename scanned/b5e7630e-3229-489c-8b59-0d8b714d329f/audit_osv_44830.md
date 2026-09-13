# [H] Snipe-IT before 8.7.0 Authorization Bypass via Livewire Snapshot Replay

## Summary
Severity: High
Advisory: CVE-2026-86746
Aliases: GHSA-jchx-hfqg-rm2m
CVSS: 7.5 (CVSS:4.0/AV:N/AC:H/AT:P/PR:L/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2026-86746
Type: osv

## Details
Snipe-IT before 8.7.0 contains an authorization bypass vulnerability in Livewire components that enforce authorization only at the route level, not within component lifecycle methods. Attackers with a valid authenticated session can replay signed component snapshots via POST /livewire/update to invoke protected methods and escalate privileges, including creating OAuth clients, minting personal access tokens, and accessing sensitive admin data.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86746.json
- https://github.com/grokability/snipe-it/security/advisories/GHSA-jchx-hfqg-rm2m
- https://nvd.nist.gov/vuln/detail/CVE-2026-86746
- https://www.vulncheck.com/advisories/snipe-it-before-8.7.0-authorization-bypass-via-livewire-snapshot-replay
