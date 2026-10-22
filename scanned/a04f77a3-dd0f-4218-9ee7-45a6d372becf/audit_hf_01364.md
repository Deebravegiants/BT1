# [H] MJR-2 Possibility to steal tokens from the contract balance

## Summary
Severity: High
Contest weight: 0.0672
Dataset id: 6945
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Method addCoverAndCreatePools defined at CoverRouter.sol#L128 accepts _protocol and collateral addresses as arguments, then call addCover that makes approve for protocol an unlimited amount of collateral tokens and call _protocol.addCover. There are no checks of protocol and collateral validity, so an attacker can pass malicious protocol and get unlimited approval of collateral tokens: if (token.allowance(address(this), spender) < _amount) { token.approve(spender, uint256(-1)); } According to the contract logic in an optimistic flow a contract shouldn't have any tokens in balance, but this invariant not fully checked, e.g. if _protocol.addCover at Rollover.sol#L75 fails and returns false, then the transaction will be executed successfully, but the user's funds will be left on the CoverRouter balance.

## Recommendation
We recommend to not use unlimited approve and add particular checks to keep the zero balance invariant.
