# [M] Static memo configuration in mpp Tempo disables per-challenge attribution binding, enabling third-party replay

## Summary
Severity: Medium
Advisory: CVE-2026-73136
Aliases: EEF-CVE-2026-73136, GHSA-34g7-vx6g-82mq
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-73136
Type: osv

## Details
Authentication Bypass by Capture-replay in ZenHive mpp allows an unauthenticated third party to obtain paid resources by replaying a transfer settled by an unrelated payer.

MPP.Methods.Tempo normally binds a settled TIP-20 TransferWithMemo to the specific challenge under verification through an attribution nonce carried in the memo. When a static "memo" is configured in method_config, check_matched_memo_binding/3 returns the match unconditionally and that binding is skipped, leaving only token, recipient, amount and the static memo value to match on. The static memo is echoed in every unauthenticated 402 response and Tempo transfers are public, so an attacker can take any matching transfer paid by a legitimate customer, request a fresh challenge for the same route, and present that transaction hash as a type="hash" credential. The hash path performs no sender or signature check tying the presenter to the wallet that broadcast the transfer.

This issue affects mpp: from 0.6.1 before 0.6.4.

## References
- https://cna.erlef.org/cves/CVE-2026-73136.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-73136
- https://repo.hex.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73136.json
- https://github.com/ZenHive/mpp/security/advisories/GHSA-34g7-vx6g-82mq
- https://nvd.nist.gov/vuln/detail/CVE-2026-73136
- https://github.com/ZenHive/mpp/commit/2207d7f456ae14c1d3fcacc6f635bf4f8cee1a34
- https://github.com/ZenHive/mpp
