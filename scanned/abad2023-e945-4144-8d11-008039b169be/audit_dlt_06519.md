# [H] Possible  to drain DepositBatch, WithdrawBatch approver's token balance due improper input validation

## Summary
Severity: High
Chain: Smart contract
Component: Velvet-Capital
Published: 2024-06-27
Source: https://github.com/hats-finance/Velvet-Capital-0x0bb0c08fd9eeaf190064f4c66f11d18182961f77/issues/78
Type: hats-finding

## Details
**Github username:** @qckhp96565463
**Twitter username:** qckhp
**Submission hash (on-chain):** 0x6583efd5a55fc239b07453ec62c92bf82ef5f65ebc0311895c1bf1b8908321a7
**Severity:** high

**Description:**
**Description**\
Possible  to drain DepositBatch, WithdrawBatch, and EnsoHandlers approver's token balance due improper input validation via DepositBatch.multiTokenSwapAndTransfer() function call. 
It's possible because of Enso's SafeEnsoShortcuts integration, it's delegate calling to any input contracts, which must not be allowed.

**Attack Scenario**\
User A wants to deposit via DepositBatch contract.
User A approves DepositBatch contract to spend his USDT tokens.
Attacker calls the DepositBatch.multiTokenSwapAndTransfer() with a malcious calldata to transferFrom USDT balance of the victim to attacker wallet.

**Attachments**

1. **Proof of Concept (PoC) File**
PoC attached.

2. **Revised Code File (Optional)**
Recommended to add some whitelisting mechanism to the target contracts and function selectors.
  
**Files:**
  - add_to_5_BatchTx.test.ts (https://hats-backend-prod.herokuapp.com/v1/files/QmV8ChEZoWuJLZqvr1fNmXanNHPiu8v5o65zP5TG4Umnnr)
