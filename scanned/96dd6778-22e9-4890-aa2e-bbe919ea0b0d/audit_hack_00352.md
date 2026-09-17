# [M] Allbridge incident: On August 19, 2026, the cross-chain bridge Allbridge was attacked. The attacker had prepared on July 26 by calling Circle’s Messag

## Summary
Severity: Medium
Target: Allbridge
Loss: $ 190,000
Attack method: Bridge Logic Flaw
Published: 2026-08-19
Source: https://x.com/SlowMist_Team/status/2090994186346790999
Type: slowmist-incident

## Details
On August 19, 2026, the cross-chain bridge Allbridge was attacked. The attacker had prepared on July 26 by calling Circle’s MessageTransmitterV2.sendMessage on Polygon to forge a CCTP-style message claiming a 1M USDC transfer (with no actual burn) and obtained a valid attestation. On Aug 19, after a real CCTP deposit brought the Base Router balance to ~191k USDC, the attacker used the forged message via receiveCctpMessage (which lacked proper verification and credited it as a real deposit), flash-loaned ~809k USDC from Aave to match the claimed amount, and withdrew ~999k USDC, netting ~$189,800.
