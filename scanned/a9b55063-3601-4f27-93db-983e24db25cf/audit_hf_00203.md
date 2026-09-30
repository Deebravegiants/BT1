# [M] `UnionToken` should check whitelist on `from`?

## Summary
Severity: Medium
Contest weight: 0.3810
Dataset id: 1075
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The `UnionToken` can check for a whitelist on each transfer in `_beforeTokenTransfer`:
```solidity
if (whitelistEnabled) {
    require(isWhitelisted(msg.sender) || to == address(0), "Whitelistable: address not whitelisted");
}
```
This whitelist is checked on `msg.sender` not on `from`, the token owner.

## Recommendation
Think about if the whitelist on `msg.sender` is correct or if it should be on `from`.

Agree with the warden findings, since `_beforeTokenTransfer` is called on all transfers (transfer and transferFrom)[https://github.com/OpenZeppelin/openzeppelin-contracts/blob/e63b09c9ad3a45484b6dc304e0e99640a9dc3036/contracts/token/ERC20/ERC20.sol#L229]

In order to enforce the whitelist you need to check against from and not msg.sender

msg.sender could be a relayer or another contract, while `from` will be the account the tokens are being moved from

Given the context and info I have this is a way to sidestep the guestList, hence a medium severity attack
