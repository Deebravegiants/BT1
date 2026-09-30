# [M] `BLOCK_PERIOD` is incorrect

## Summary
Severity: Medium
Contest weight: 0.5458
Dataset id: 17005
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
[Config.sol#L47](https://github.com/code-423n4/2022-10-zksync/blob/456078b53a6d09636b84522ac8f3e8049e4e3af5/ethereum/contracts/zksync/Config.sol#L47)  

The `BLOCK_PERIOD` is set to 13 seconds in `Config.sol`.
    
```solidity
uint256 constant BLOCK_PERIOD = 13 seconds;
```

Since moving to Proof-of-Stake (PoS) after the Merge, block times on ethereum are fixed at 12 seconds per block (slots). <https://ethereum.org/en/developers/docs/consensus-mechanisms/pos/#:~:text=Whereas%20under%20proof%2Dof%2Dwork,block%20proposer%20in%20every%20slot>.

## Recommendation
Change the block period to be 12 seconds
    
```solidity
uint256 constant BLOCK_PERIOD = 12 seconds;
```

This is a valid medium issue! Thanks!

The warden has shown how, due to an incorrect configuration, L2Transactions will expire earlier than intended.

The value would normally be rated a Low Severity, however, because the Warden has shown a more specific impact, I agree with Medium Severity.
