# [M] use `safeTransfer` instead of just `transfer`

## Summary
Severity: Medium
Chain: Smart contract
Component: Inverter-Network
Published: 2024-06-05
Source: https://github.com/hats-finance/Inverter-Network-0xe47e52c4fea05e555920f1dcdcc6fb8eca103eeb/issues/10
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0xe2145361eb26f0e47c1ff1d31579e8342dddef8453bca0d73bc04d3ac128d8eb
**Severity:** medium

**Description:**
**Description**\
Failed transfers are not handled. Using `safeTransfer` instead of just transfer is prone to issues where some tomes return false instead of reverting. So this is an issue for all the collateral tokens that return false instead of reverting when transferring tokens.

Previous issues:

1. <https://github.com/sherlock-audit/2023-01-cooler-judging/issues/335>
2. <https://solodit.xyz/issues/m-10-use-safetransfersafetransferfrom-consistently-instead-of-transfertransferfrom-code4rena-trader-joe-trader-joe-contest-git>
3. <https://solodit.xyz/issues/m-03-use-safetransfersafetransferfrom-instead-of-transfertransferfrom-code4rena-rubicon-rubicon-contest-git>

**Attack Scenario**\
Look at line233,
Tokens not compliant with the ERC20 specification could return false from the transfer function call to indicate the transfer fails, while the calling contract would not notice the failure if the return value is not checked. Checking the return value is a requirement, as written in the EIP-20 specification:

Callers MUST handle false from returns (bool success). Callers MUST NOT assume that false is never returned!

So use `safeTransfe`r instead of just transfer.

```solidity
src\modules\fundingManager\bondingCurve\abstracts\RedeemingBondingCurveBase_v1.sol

158:     function _sellOrder(
...SNIP...
162:     )
163:         internal
164:         returns (uint totalCollateralTokenMovedOut, uint issuanceFeeAmount)
165:     {
...SNIP...
200:         IERC20 collateralToken = __Module_orchestrator.fundingManager().token();
201: 
...SNIP...

233:   >>>   collateralToken.transfer(_receiver, collateralRedeemAmount);
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Inverter-Network-0xe47e52c4fea05e555920f1dcdcc6fb8eca103eeb/issues/10_
