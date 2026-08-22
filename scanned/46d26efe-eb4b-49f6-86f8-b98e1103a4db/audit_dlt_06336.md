# [M] Protocol will not work with tokens that do not return bool value on approve calls

## Summary
Severity: Medium
Chain: Smart contract
Component: Blast-Futures-Exchange
Published: 2024-02-09
Source: https://github.com/hats-finance/Blast-Futures-Exchange-0x97895c329b950755566ddcdad3395caaea395074/issues/56
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0x059169db82ba34561195e8796e8fded847e14db63af3ce3d094228c29329ad30
**Severity:** medium

**Description:**
**Description**\
The protocol is intended to work with any ERC20 compatible tokens and even with some incompatible i.e. tokens that do not return a `bool` value when calling some of their functions such as `transfer` or `transferFrom` directly. This is achieved by utilizing low-level calls within the transfer functions implemented in the protocol. However within the `BfxVault.sol` contract we have the `makeDeposit()` function that is callable only by users with `TREASURER_ROLE`. This function calls an internal `_doDeposit()` function which executes two steps:
1. Approves the BFX contract to spend a desired amount
2. Invokes the `deposit()` function on the BFX contract which transfers the provided amount from the BfxVault contract.

In order for the execution to happen properly the TRASURER has to transfer the specified amount before invoking the `makeDeposit()` function. 

The vulnerability here presents itself during the execution of `makeDeposit()` where a call is made to `paymentToken.approve()`, where `paymentToken` is wrapped with the IERC20 interface. However for tokens that do not return a `bool` value when calling approve such as USDT on Ethereum, the transaction will revert with an EVM error.

I am considering this issue with Medium severity due to the possibility of the owner to retrieve those tokens by invoking `withdrawTokensTo()`.

**Attack Scenario**\

If `paymentToken` is set to USDT or any other token that do not return a `bool` value when `approve()` function is called, the TREASURER of the BfxVault will not be able to make a deposit from the vault to the Bfx Exchange due to failure in the `makeDeposit()` function execution.

**Attachments**

1. **Proof of Concept (PoC) File**
The `BfxVault.t.sol` is the PoC for the discovered issue. Steps to run it:
- Add the file to the `test` folder
- Add an RPC url as a local env variable called `ETH_RPC_URL`
- Run the test with `forge test --match-contract BfxFail --fork-url $ETH_RPC_URL -vv`
- You should see a failed test with `EvmError: Revert` message
2. **Revised Code File (Optional)**
- Added a `_makeApprove` internal function which utilizes low-level calls similar to `_makeTransfer` and `_makeTransferFrom`
- Optional: You can also add a `_makeApprove` call to set the approval to 0 in order to avoid future issues with tokens that require approval to 0 first
  
**Files:**
  - BfxVault.t.sol (https://hats-backend-prod.herokuapp.com/v1/files/QmZR6FfhbRNn99KFkdnxc99p8udX2BLZkRGGatgbWiz6S1)
  - BfxVault.sol (https://hats-backend-prod.herokuapp.com/v1/files/QmciFNcsN8nq4kjJ1CZYaviJV3B73xrrV3JMC5XK9Nen7q)
