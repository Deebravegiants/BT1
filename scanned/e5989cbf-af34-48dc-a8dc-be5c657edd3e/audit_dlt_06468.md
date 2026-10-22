# [H] `Usdo.send` will run out of gas

## Summary
Severity: High
Chain: Smart contract
Component: Tapioca--Lending-Engine-
Published: 2024-06-06
Source: https://github.com/hats-finance/Tapioca--Lending-Engine--0x5bee198f5b060eecd86b299fdbea6b0c07c728dd/issues/22
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0x207e30afed3ddf67046e6d01240e28122b7b3dbc796c13a9b795c73c8092aaf9
**Severity:** high

**Description:**
**Description**\
In function [Usdo.send](https://github.com/hats-finance/Tapioca--Lending-Engine--0x5bee198f5b060eecd86b299fdbea6b0c07c728dd/blob/8920782db6044643fd0c682f58ef37f7e59f99b1/contracts/usdo/Usdo.sol#L199-L207), it looks that the function keeps calling itself and until runs out of gas, which isn't supposed to be right

**Attack Scenario**\
 [Usdo.send](https://github.com/hats-finance/Tapioca--Lending-Engine--0x5bee198f5b060eecd86b299fdbea6b0c07c728dd/blob/8920782db6044643fd0c682f58ef37f7e59f99b1/contracts/usdo/Accordin to Usdo.sol#L199-L207)'s defination, it keeps calling itself.
```solidity
198     /// @dev override default `send` behavior to add `whenNotPaused` modifier
199     function send(SendParam calldata _sendParam, MessagingFee calldata _fee, address _refundAddress)
200         external
201         payable
202         override
203         whenNotPaused
204         returns (MessagingReceipt memory msgReceipt, OFTReceipt memory oftReceipt)
205     {
206         (msgReceipt, oftReceipt) = this.send(_sendParam, _fee, _refundAddress);
207     }
```

**Attachments**

1. **Proof of Concept (PoC) File**
<!-- You must provide a file containing a proof of concept (PoC) that demonstrates the vulnerability you have discovered. -->

2. **Revised Code File (Optional)**
<!-- If possible, please provide a second file containing the revised code that offers a potential fix for the vulnerability. This file should include the following information:
- Comment with a clear explanation of the proposed fix.
- The revised code with your suggested changes.
- Any additional comments or explanations that clarify how the fix addresses the vulnerability. -->
