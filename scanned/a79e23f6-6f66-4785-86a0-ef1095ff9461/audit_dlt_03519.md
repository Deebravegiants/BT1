# [H] Unrestricted `addLiquidity` could cause unintended results on front-end apps that listen to events.

## Summary
Severity: High
Chain: Smart contract
Component: 2021-04-vader
Published: 2021-04-28
Source: https://github.com/code-423n4/2021-04-vader-findings/issues/317
Type: code-finding

## Details
# Handle

shw


# Vulnerability details

## Impact

The `addLiquidity` function in `Pool.sol` lacks an access control, which allows an attacker to add liquidity for any specific user. Front-end apps that listen to `AddLiquidity` events may be affected by this vulnerability and may go wrong since it is not the user's intent to add liquidity.

## Proof of Concept

Referenced code:
Pool.sol#L54-L75](https://github.com/code-423n4/2021-04-vader/blob/main/vader-protocol/contracts/Pools.sol#L54-L75)

PoC: [Link to PoC](https://drive.google.com/drive/folders/1W3jhlWIIh7FxTLZET3z49yA0DBvlbcPg?usp=sharing)
See the file `302_addLiquidity.js` for a PoC of this attack. To run it, use `npx hardhat test 302_addLiquidity.js`.

## Tools Used

None

## Recommended Mitigation Steps

Consider checking whether `addLiquidity` is called from the router. If not, then the transaction should revert. Add another function, e.g., `addLiquidityDirectly`, for end users if they want to interact with the pool to add liquidity directly.
