# [H] RetoSwap incident: RetoSwap (a Tor-based P2P multisig DEX powered by the Haveno trade protocol for trading Monero) was actively exploited. Attackers

## Summary
Severity: High
Target: RetoSwap
Loss: $ 2,700,000
Attack method: Protocol Logic Vulnerability
Published: 2026-05-20
Source: https://x.com/retoswap/status/2056984875383632226?s=46&amp;t=DLwbX9Nw4QECiyZQ0av-fg
Type: slowmist-incident

## Details
RetoSwap (a Tor-based P2P multisig DEX powered by the Haveno trade protocol for trading Monero) was actively exploited. Attackers sent fake, out-of-order ACK messages impersonating the arbitrator during ongoing trades. This tricked the client into updating the arbitrator’s node address to the attacker’s controlled address, allowing them to create a compromised multisig wallet before the victim deposited funds. The exploit mainly affected crypto-to-crypto trades. RetoSwap immediately banned the attacker’s onion address, forced a client version update to halt all trading, and is working on a patch and potential recovery for affected users. Approximately 7,000 XMR were stolen.
