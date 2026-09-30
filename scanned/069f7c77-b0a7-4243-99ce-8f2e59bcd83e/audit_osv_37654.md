# [H] Nimiq: Remote crash via off-by-one signer bounds check in proposal buffer

## Summary
Severity: High
Advisory: CVE-2026-32605
Aliases: GHSA-g99c-h7j7-rfhv
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-13
Source: https://osv.dev/vulnerability/CVE-2026-32605
Type: osv

## Details
nimiq/core-rs-albatross is a Rust implementation of the Nimiq Proof-of-Stake protocol based on the Albatross consensus algorithm. Prior to version 1.3.0, an untrusted peer could crash a validator by publishing a signed tendermint proposal message where signer == validators.num_validators(). ProposalSender::send uses > instead of >= for the signer bounds check, so the equality case passes and reaches validators.get_validator_by_slot_band(signer), which panics with an out-of-bounds index before any signature verification runs. This issue has been fixed in version 1.3.0.

## References
- https://github.com/nimiq/core-rs-albatross/releases/tag/v1.3.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32605.json
- https://github.com/nimiq/core-rs-albatross/security/advisories/GHSA-g99c-h7j7-rfhv
- https://nvd.nist.gov/vuln/detail/CVE-2026-32605
- https://github.com/nimiq/core-rs-albatross/commit/9199364b60c7acae4219800d194bbe07d2997b8c
- https://github.com/nimiq/core-rs-albatross/pull/3661
