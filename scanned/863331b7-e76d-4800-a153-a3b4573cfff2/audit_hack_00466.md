# [M] Singularity Finance incident: Singularity Finance vaults were exploited due to a critical oracle misconfiguration. The admin had registered an unsupported Unisw

## Summary
Severity: Medium
Target: Singularity Finance
Loss: $ 413,000
Attack method: Oracle Misconfiguration
Published: 2026-04-27
Source: https://x.com/0xSalazar/status/2048762346143666656
Type: slowmist-incident

## Details
Singularity Finance vaults were exploited due to a critical oracle misconfiguration. The admin had registered an unsupported Uniswap V3 fee tier of 42 (valid tiers: 100/500/3000/10000) back in January, causing factory.getPool() to silently return address(0). This made the oracle price all non-USDC reserves at zero. The vault only recognized ~$100 in idle USDC while real yield tokens sat undervalued. The attacker flash-loaned 100K USDC from Morpho, deposited into the vault to mint ~99.99% of shares at the broken ratio, then redeemed for a proportional share of actual underlying assets, draining ~$413K. Root cause: admin parameter error combined with missing input validation on fee tiers. The misconfig sat undetected for ~3 months.
