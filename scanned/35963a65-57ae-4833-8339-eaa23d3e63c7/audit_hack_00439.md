# [M] WUSD.fi / GLOVE incident: WUSD.fi / GLOVE on Ethereum suffered an incentive abuse exploit. The attacker exploited the lack of Sybil resistance in the WUSD._

## Summary
Severity: Medium
Target: WUSD.fi / GLOVE
Loss: $ 200,000
Attack method: Sybil Attack
Published: 2026-05-25
Source: https://x.com/exvulsec/status/2058803971947385330
Type: slowmist-incident

## Details
WUSD.fi / GLOVE on Ethereum suffered an incentive abuse exploit. The attacker exploited the lack of Sybil resistance in the WUSD._englove reward path. By using EIP-7702 helper contracts and a Morpho USDT flash loan to repeatedly wrap/unwrap at least 100 WUSD (with fresh addresses holding <2 GLOVE), they harvested nearly 2 GLOVE per cycle, dumped the GLOVE into Uniswap V3 pools, and drained ~$200K in USDC/USDT from the liquidity pools.
