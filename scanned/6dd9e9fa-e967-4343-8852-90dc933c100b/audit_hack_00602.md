# [C] GMX incident: On July 9, according to monitoring by MistTrack’s MistEye security system, the well-known decentralized trading platform GMX (@GMX

## Summary
Severity: Critical
Target: GMX
Loss: $ 42,000,000
Attack method: Contract Vulnerability
Published: 2025-07-09
Source: https://x.com/SlowMist_Team/status/1942949653231841352
Type: slowmist-incident

## Details
On July 9, according to monitoring by MistTrack’s MistEye security system, the well-known decentralized trading platform GMX (@GMX_IO) suffered an attack, resulting in asset losses exceeding $42 million.

Analysis indicates that the core of this attack lies in the exploitation of two features: the use of leverage when the Keeper system executes orders, and the update mechanism where the global average price adjusts during shorting operations but does not update when closing short positions. Leveraging these mechanics, the attacker conducted a reentrancy attack to create large short positions, manipulating the global short average price and the size of the global short position. This, in turn, artificially inflated the price of GLP, which the attacker then redeemed for profit. Following negotiation, the attacker returned all stolen funds and received a $5 million bounty.
