# [H] Incentive mechanism doesn't work on Arbitrum

## Summary
Severity: High
Chain: Smart contract
Component: Catalyst-Exchange
Published: 2024-01-26
Source: https://github.com/hats-finance/Catalyst-Exchange-0x3026c1ea29bf1280f99b41934b2cb65d053c9db4/issues/50
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** https://twitter.com/windhustler
**Submission hash (on-chain):** 0x5affa9ba62c91d0fa1e633b336f88d94167b33dcca92ae9c5e0ab3e26af0f213
**Severity:** high

**Description:**
**Description**\
The incentive structure is broken on Arbitrum. The relayer is getting underpaid for the work he's doing.
As the main point of the codebase is to provide incentives and it doesn't work on Arbitrum, I'm marking this as high severity.


**Attack Scenario**\
Gas on Arbitrum is handled differently than on other chains. 

Here is an explanation of how gas works on Arbitrum: https://docs.arbitrum.io/devs-how-tos/how-to-estimate-gas.

The summary is that the transaction fee is a function of:

- Gas price of L2(Arbitrum).
- Gas used on L2(Arbitrum).
- L1 price per byte of data.
- Size of the calldata.

This is the formula used to compute the transaction fee:

`L1 Estimated Cost (L1C) = L1 price per byte of data (L1P) * Size of data to be posted in bytes (L1S)`

`Extra Buffer (B) = L1 Estimated Cost (L1C) / L2 Gas Price (P)`

`TXFEES = P * (L2G + ((L1P * L1S) / P))`

What is important to note here gas used on Arbitrum is the same as you would use on Ethereum. It's the same EVM opcodes. 
What is different is the final transaction fee that includes the L1 portion. 

**Issue**

The execution on the receiving side inside the `processPacket` starts by taking note of the gas at the beginning of the function execution: https://github.com/catalystdao/GeneralisedIncentives/blob/main/src/IncentivizedMessageEscrow.sol#L243
And at the end of the function, it computes the total gas used. This is being sent with the acknowledgment back to the sending chain so that the relayer can be paid from the Incentive deposited by the application: https://github.com/catalystdao/GeneralisedIncentives/blob/main/src/IncentivizedMessageEscrow.sol#L329

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Catalyst-Exchange-0x3026c1ea29bf1280f99b41934b2cb65d053c9db4/issues/50_
