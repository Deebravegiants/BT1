# [H] Ticket duplication

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description
`Ticket._beforeTokenTransfer()` contains logic to update the `SortitionSumTree` from which prize winners are drawn. In the case where the `from` address is the same as the `to` address, tickets are duplicated rather than left unchanged. This allows any attacker to duplicate their tickets with no limit and virtually guarantee that they will win all awarded prizes.


**code/pool/contracts/token/Ticket.sol:L71-L79**
```solidity
if (from != address(0)) {
  uint256 fromBalance = balanceOf(from).sub(amount);
  sortitionSumTrees.set(TREE_KEY, fromBalance, bytes32(uint256(from)));
}

if (to != address(0)) {
  uint256 toBalance = balanceOf(to).add(amount);
  sortitionSumTrees.set(TREE_KEY, toBalance, bytes32(uint256(to)));
}
```

This code was outside the scope of our review but was live on mainnet at the time the issue was disovered. We immediately made the client aware of the issue and an effort was made to mitigate the impact on the existing deployment.
