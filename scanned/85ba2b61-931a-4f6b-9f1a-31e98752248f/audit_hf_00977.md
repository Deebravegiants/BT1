# [H] Misjudgment regarding reentrancy risks associated with ERC777 tokens can lead to direct theft of funds

## Summary
Severity: High
Contest weight: 0.5996
Dataset id: 3041
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
ERC777 tokens enable multiple reentrancy attacks. The vulnerability stems from the fact that ERC777 tokens, unlike ERC1155 and ERC721 tokens, allow the from address of a transfer to get a callback, which introduces an additional attack surface that has been unaccounted for with ERC777 tokens. This has been confirmed during consultation with the client. However, that's not true, ERC777 tokens have a tokensToSend hook that allows the from address of a transfer to get a callback. Here's a reference to an ERC777 implementation: https://github.com/Switcheo/switcheo-eth/blob/master/contracts/lib/token/ERC777/ERC777.sol
```solidity
function transferFrom(address holder, address recipient, uint256 amount) external returns (bool) {
    require(recipient != address(0), "ERC777: transfer to the zero address");
    require(holder != address(0), "ERC777: transfer from the zero address");
    address spender = msg.sender;
    _callTokensToSend(spender, holder, recipient, amount, "", "");
    _move(spender, holder, recipient, amount, "", "");
    _approve(holder, spender, _allowances[holder][spender].sub(amount));
    _callTokensReceived(spender, holder, recipient, amount, "", "", false);
    return true;
}
```
There are three separate vulnerabilities arising from this misconception about ERC777 tokens in the codebase, so we'll go through them one by one: Let's take a look at LendingPool.donateToTranche().

## Recommendation
The mitigation for the inflation attack:
