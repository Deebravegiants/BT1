# [H] _recipient can reenter the withdraw function

## Summary
Severity: High
Chain: Smart contract
Component: ether-fi
Published: 2023-11-06
Source: https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/issues/6
Type: hats-finding

## Details
**Github username:** --
**Submission hash (on-chain):** 0x26361656404c6c1b17e5a2cee60e3e4f891ec6caa7061603989d60fbd69dbffa
**Severity:** high

**Description:**
**Description**\
There is no check if the _recipient address is a contract or an EOA. If it’s a contract, _recipient can call back into the withdraw function and drain the LiquidityPool contract.

**Attack Scenario**\
_recipient can drain LiquidityPool contract

**Attachments**
https://github.com/GadzeFinance/dappContracts/blob/68bf2597086d9aa39968c504f04cf34aa0f864c0/src/LiquidityPool.sol#L163-L181

**Recommendation**\
Use ReentrancyGuard to protect against reentrancy
