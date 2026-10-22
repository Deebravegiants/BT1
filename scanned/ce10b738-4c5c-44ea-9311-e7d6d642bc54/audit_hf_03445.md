# [M] Corruption of oracle data

## Summary
Severity: Medium
Contest weight: 0.3882
Dataset id: 18846
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The contract implements a price oracle that aggregates price arrays submitted by off‑chain nodes for a specific reporting block. The vulnerability stems from the fact that the implementation stores the price array in a single storage variable that is reused for every reporting period, without any explicit association between the array contents and the block number they belong to. Because the code does not verify that the incoming data corresponds to the current epoch block before overwriting the array, price values from two distinct blocks can be mixed together. When a node pushes data for block 14400 while another node later pushes data for block 21600, both sets of values are appended to the same array, resulting in a corrupted price list that contains a blend of old and new prices. Moreover, when the older block is finally finalised, the contract deletes the entire array, unintentionally discarding the newer block’s data as well. This flaw was discovered during a manual audit where a proof‑of‑concept test set the last reported block to 7200, advanced the blockchain to block 21601 and observed that the oracle stored entries for both block 14400 and block 21600 in the same array, then lost the later data after the earlier block was finalised. The issue is difficult to notice because the contract does not emit an explicit error; the array simply appears to contain price data, but the values no longer correspond to the expected reporting block, leading to silent mispricing. An attacker can exploit this by submitting a valid price report for a stale block while the contract is still awaiting data for a newer block, causing the price feed used by downstream contracts to be based on mixed or outdated values. This can result in incorrect calculations for collateral, liquidations, or reward distributions, potentially causing users to receive zero or incorrect refunds, see their balances unexpectedly unchanged, or suffer loss of funds due to mis‑priced trades. The bug violates the fundamental accounting assumption that each price report is uniquely tied to a single block epoch. To remediate the issue, the contract should enforce that only data for the latest reportable block is accepted, for example by checking that the reportingBlockNumber matches the current epoch block before writing to storage. Additionally, price arrays should be stored in a mapping keyed by block number (e.g., mapping(uint256=>uint256[]) blockPrices) or the previous array should be explicitly deleted when a new block’s data is pushed, ensuring that data from different epochs never intermingle.

## Proof of Concept
Block for `lastReportedSDPriceData` = 7200  
Let’s make the current block = 21601  
Now `StaderOracle` will have data for 14400 and 21600, both blocks are being pushed by nodes and in the prices array.  
It will be all mixed up. Also, As soon as the 14400 block is finalised, the data for block 21600 is all lost as well.

## Recommendation
Add `if (_sdPriceData.reportingBlockNumber == getSDPriceReportableBlock())` to ensure it is always the latest reportable block data.  
Add `mapping(uint256 => uint256[]) blockPrices` to store the prices array separately for each block being reported, to avoid mixing and corruption of data. Or have `uint256 currentEpochBlock`, so when a new block of data is pushed, previous data is deleted before pushing the new data.

```solidity
if(_sdPriceData.reportingBlockNumber!=currentEpochBlock){
   delete prices;
}
```
