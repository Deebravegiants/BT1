# [M] A user can inflate their NFT balance

## Summary
Severity: Medium
Contest weight: 0.6006
Dataset id: 8580
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a user is using the ERC20 call of transferring tokens (transfer or transferFrom) the ERC20 balance changes are synced to ERC1155 balance changes in _transfer:
File: Groge.sol
```solidity
372: uint256 balanceBeforeSender = _balances[from];
373: uint256 balanceBeforeReceiver = _balances[to];
374:
375: if (!isInAllowlist(from)) {
376:     uint256 tokens_to_burn = (balanceBeforeSender / 10 ** _decimals) - ((balanceBeforeSender - value) / 10 ** _decimals);
377:     _nft_burn(from, 0, tokens_to_burn);
378: }
379:
380: if (!isInAllowlist(to)) {
381:     uint256 tokens_to_mint = ((balanceBeforeReceiver + value) / 10 ** _decimals) - (balanceBeforeReceiver / 10 ** _decimals);
382:     _nft_mint(to, 0, tokens_to_mint);
383: }
384:
385: _update(from, to, value);
```
The issue above is that the old state of balanceBeforeReceiver is used to determine how many nfts should be minted. If a user does a transfer to themselves that is low enough to not decrease their tokens_to_burn but high enough to increase their tokens_to_mint they will be able to inflate their nft balance: Alice has 1.9e18 ERC20 tokens. She transfers 0.2e18 tokens to herself so both balanceBeforeSender/Receiver are 1.9e18. tokens_to_burn will not decrease as 1.9e18/1e18 - 1.7e18/1e18 => 1 - 1 = 0. But, tokens_to_mint will increase as 2.1e18/1e18 - 1.9e18/1e18 => 2 - 1 = 1 Hence after the transfer, Alice will still have an ERC20 balance of 1.9e18 but 2 nfts. This could be repeated for as many times as you want. Since all the balance is kept in the ERC20 token balance representation this will not affect anything more than the nft balance representation. If Alice would try to transfer her two nfts it would revert as she hasn't got 2e18 ERC20 tokens to transfer. This also works in the other direction. A user could artificially decrease their nft balance by doing a transfer to themselves. Do the same scenario as above but Alice starts with 1.1e18 tokens. Then she would end up with no nfts but 1.1e18 tokens after transferring 0.2e18 tokens to herself.
Groge_Report.md

## Recommendation
Consider doing the balance changes before the balance sync, then using the changed values to calculate the difference:
```solidity
uint256 balanceBeforeSender = _balances[from];
uint256 balanceBeforeReceiver = _balances[to];
+ _update(from, to, value);
if (!isInAllowlist(from)) {
    uint256 tokens_to_burn = (balanceBeforeSender / 10 ** _decimals) - (_balances[from] / 10 ** _decimals);
    _nft_burn(from, 0, tokens_to_burn);
}
if (!isInAllowlist(to)) {
    uint256 tokens_to_mint = (_balances[to] / 10 ** _decimals) - (balanceBeforeReceiver / 10 ** _decimals);
    _nft_mint(to, 0, tokens_to_mint);
}
- _update(from, to, value);
```
