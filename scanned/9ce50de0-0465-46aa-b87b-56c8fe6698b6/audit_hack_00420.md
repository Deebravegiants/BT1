# [M] Flooring Protocol & BitmapPunks incident: Flooring Protocol V2 and BitmapPunks (BT404 / $BMP) were exploited due to a BT404-style packed ownership logic vulnerability (mali

## Summary
Severity: Medium
Target: Flooring Protocol & BitmapPunks
Loss: -
Attack method: Smart Contract Vulnerability
Published: 2026-06-08
Source: https://x.com/mfigge/status/2063782936399544740
Type: slowmist-incident

## Details
Flooring Protocol V2 and BitmapPunks (BT404 / $BMP) were exploited due to a BT404-style packed ownership logic vulnerability (malicious high-bit token ID alias + unchecked integer underflow). The attacker minted near-infinite fpTokens/$BMP with a dust amount of WETH, drained liquidity pools, and extracted high-value NFTs (e.g., BAYC, CryptoPunks) at low cost. Yuga Labs quickly intervened with a white-hat operation via GrailsOTC, rescuing 68 NFTs worth over $500,000, now held safely for return after fixes.
