# [M] M-2 CurveLPOracle is not working

## Summary
Severity: Medium
Contest weight: 0.0601
Dataset id: 6752
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
• GenericOracle.sol#L34
_chainlinkOracle is the first in sequence in GenericOracle.getUSDPrice.
Since there is already a crvUSD oracle on the mainnet, CurveLPOracle will never be used. Current Aggregator on mainnet for crvUSD: 0x145f040dbCDFf4cBe8dEBBd58861296012fCB269 (https://data.chain.link/ethereum/mainnet/stablecoins/crvusd-usd).

## Recommendation
We recommended reprioritising the selection of Oracles (customOracles should be first). If necessary
