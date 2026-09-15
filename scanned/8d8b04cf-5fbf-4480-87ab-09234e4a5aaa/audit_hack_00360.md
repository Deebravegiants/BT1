# [M] Coreum Bridge incident: On August 9, 2026, the cross-chain bridge connecting the XRP Ledger and Coreum (now tx) was exploited. The attacker abused a flaw

## Summary
Severity: Medium
Target: Coreum Bridge
Loss: $ 200,000
Attack method: Bridge Logic Vulnerability
Published: 2026-08-09
Source: https://x.com/txEcosystem/status/2087269579190046895
Type: slowmist-incident

## Details
On August 9, 2026, the cross-chain bridge connecting the XRP Ledger and Coreum (now tx) was exploited. The attacker abused a flaw in the deposit-verification/relayer logic by creating fake deposits (self-transfers of the bridge’s own wrapped tokens with valid memos), tricking the relayers into authorizing real XRP withdrawals from the bridge’s reserve. Nearly 200,000 XRP (~$200,000) was drained in 94 multisig transactions over 97 minutes.
