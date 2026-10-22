# [M] On-chain transfer proof is not single-use in mpp EVM payment method, enabling cross-challenge replay

## Summary
Severity: Medium
Advisory: CVE-2026-67581
Aliases: EEF-CVE-2026-67581, GHSA-vp5h-xh25-44wf
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-67581
Type: osv

## Details
Authentication Bypass by Capture-replay in ZenHive mpp allows an unauthenticated remote client to obtain paid resources by resubmitting one settled on-chain transfer.

MPP.Methods.EVM.verify/2 accepts a transaction-hash credential and matches a transfer purely on token, to and amount (ERC-20) or to and value (native). It binds the proof neither to the challenge being verified nor to any record of prior use, and the generic MPP.Plug dedup store keys on challenge.id, which is regenerated for every 402 response. On a static-price route, a single historical transfer matching the charge therefore satisfies an unbounded number of later charges, including transfers an attacker can read off a public block explorer.

This issue affects mpp: from 0.3.0 before 0.6.3.

## References
- https://cna.erlef.org/cves/CVE-2026-67581.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-67581
- https://repo.hex.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/67xxx/CVE-2026-67581.json
- https://github.com/ZenHive/mpp/security/advisories/GHSA-vp5h-xh25-44wf
- https://nvd.nist.gov/vuln/detail/CVE-2026-67581
- https://github.com/ZenHive/mpp/commit/ecc038088b1cda09ad8a84acc6cc112addb4a68f
- https://github.com/ZenHive/mpp
