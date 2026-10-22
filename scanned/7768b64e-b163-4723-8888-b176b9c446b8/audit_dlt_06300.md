# [M] Large approvals may not work with some ERC20 tokens

## Summary
Severity: Medium
Chain: Smart contract
Component: Ion-Protocol
Published: 2024-01-22
Source: https://github.com/hats-finance/Ion-Protocol-0x20c44e7b618d58f9982e28de66d8d6ee176eb481/issues/8
Type: hats-finding

## Details
**Github username:** @saidqayoumsadat
**Twitter username:** saqsadat143
**Submission hash (on-chain):** 0x29bca613cdc09f2a8f373b03f6960a43c19e663395c840fb2f0d6f0d151115bc
**Severity:** medium

**Description:**
**Description**\
Not all IERC20 implementations are totally compliant, and some (e.g UNI, COMP) may fail if the valued passed is larger than uint96. 

Source: https://github.com/d-xo/weird-erc20#revert-on-large-approvals--transfers


1. **Proof of Concept (PoC) File**


```solidity

110        IERC20(ilkAddress).approve(address(_gemJoin), type(uint256).max);

        IERC20(address(LST_TOKEN)).approve(address(VAULT), type(uint256).max);

```
https://github.com/Ion-Protocol/ion-protocol/blob/aa3bf58a6343edb8212574ea9ad6311e6e6aaa1a/src/flash/handlers/base/IonHandlerBase.sol#L101C1-L101C74

```solidity

58        IERC20(address(LST_TOKEN)).approve(address(VAULT), type(uint256).max);

```
https://github.com/Ion-Protocol/ion-protocol/blob/aa3bf58a6343edb8212574ea9ad6311e6e6aaa1a/src/flash/handlers/base/UniswapFlashloanBalancerSwapHandler.sol#L58C1-L58C79
