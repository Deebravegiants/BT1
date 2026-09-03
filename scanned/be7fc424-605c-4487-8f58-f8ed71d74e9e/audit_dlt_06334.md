# [M] Solmate safeTransferLib.sol functions does not check the codesize of the token address, which may lead to fund loss

## Summary
Severity: Medium
Chain: Smart contract
Component: Catalyst-Exchange
Published: 2024-01-24
Source: https://github.com/hats-finance/Catalyst-Exchange-0x3026c1ea29bf1280f99b41934b2cb65d053c9db4/issues/6
Type: hats-finding

## Details
**Github username:** @0xRizwann
**Twitter username:** 0xRizwann
**Submission hash (on-chain):** 0x71c360d0e976cf6143c689dc503016878ff8709f92991c878e5bf3e67073314c
**Severity:** medium

**Description:**
**Description**

In CatalystFactory.sol contract, deployVault function is used to deploy the catalyst vault and then it funds the vault with tokens. The function has used `safeTransferFrom` from solmate's `safeTransferLib.sol` to send the tokens to vault.

```solidity

        for (uint256 it; it < assets.length;) {
            ERC20(assets[it]).safeTransferFrom(    
                msg.sender,
                vault,
                init_balances[it]
            );
```

The used safeTransferFrom() function from solmate library which doesn't **check the existence of code at the token address**. This is a known issue while using solmate's libraries.

Per the Solmate safeTransferLib.sol,

> Note that none of the functions in this library check that a token has code at all! .....

Hence using safeTransferLib.sol library may lead to miscalculation of funds and may lead to loss of funds , because if safeTransferFrom() are called on a token address that doesn't have contract in it, it will always return success, bypassing the return value check. Due to this protocol will think that funds has been transferred to vault by vault deployer and the transaction is successful , and records will be accordingly calculated, but **in reality funds were never been transferred.**

`safeTransferFrom()` function under the hood uses low level call function which can be checked here

However, solidity documentation strictly warns that,

> The low-level functions call, delegatecall and staticcall return true as their first return value if the account called is non-existent, as part of the design of the EVM. Account existence must be checked prior to calling if needed.

code existence must be checked especially for low level functions like call,staticcall and delegatecall.

**Openzeppelin and Solady confirms this and comply this requirements in their library, only solmate does not check code existence.**


_Trimmed to 38 lines — full report: https://github.com/hats-finance/Catalyst-Exchange-0x3026c1ea29bf1280f99b41934b2cb65d053c9db4/issues/6_
