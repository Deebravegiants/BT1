# [M] ERC420.setAllowList() can replicate the previous target state

## Summary
Severity: Medium
Contest weight: 0.5813
Dataset id: 8581
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The ERC420 contract owner can add/remove accounts from/to the allowList, and if an account is added to the allowList (where the state == true); then his NFTs will be burnt, and if an account is removed from the allowList (where the state == false) then he will be minted NFTs equivalent to his balance of tokens (balance / 1e18). But it was noticed that the setAllowList() function misses checking if the new state is different from the currently assigned one, so if the current state of the target was set previously to false (where this target has previously minted NFTs when changing his state), then if the owner re-sets the target's state again to false; the target will be again minted NFTs equivalent to his current tokens balance. Same issue if the target's previous state was true (the target is in the allowList), where his tokens can be burnt twice if the owner calls setAllowList() without changing the target's state (note: due to another vulnerability; the target can be minted tokens even if he's in the allowList via safeBatchTransferFrom() function as it doesn't check for the receiver being allowListed or not before minting him NFTs).
Code Snippet
ERC420.setAllowList function
```solidity
_allowList[target] = state;
uint256 balance = _balances[target];
if (state) {
    uint256 tokens_to_burn = balance / 10 ** _decimals;
    _nft_burn(target, 0, tokens_to_burn);
} else {
    uint256 tokens_to_mint = balance / 10 ** _decimals;
    _nft_mint(target, 0, tokens_to_mint);
```

## Recommendation
Update setAllowList() to check if the new state is different from the currently assigned one:
```solidity
+ require(_allowList[target] != state,"assigning the same state is not allowed");
_allowList[target] = state;
uint256 balance = _balances[target];
if (state) {
    uint256 tokens_to_burn = balance / 10 ** _decimals;
    _nft_burn(target, 0, tokens_to_burn);
} else {
    uint256 tokens_to_mint = balance / 10 ** _decimals;
    _nft_mint(target, 0, tokens_to_mint);
```
