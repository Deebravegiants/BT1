# [M] Permit calls can be front-ran and user deposits can be DoSed

## Summary
Severity: Medium
Chain: Smart contract
Component: Velvet-Capital
Published: 2024-06-20
Source: https://github.com/hats-finance/Velvet-Capital-0x0bb0c08fd9eeaf190064f4c66f11d18182961f77/issues/5
Type: hats-finding

## Details
**Github username:** @PlamenTSV
**Twitter username:** @p_tsanev
**Submission hash (on-chain):** 0xf98d2120ea46222a13763c76ebddd6f7014b02038d01c3b1440d8c60e5c7f4b2
**Severity:** medium

**Description:**
**Description**\
The ``VaultManager.sol`` contract features several functions allowing users to grant ERC20 permits to grant allowance to other users to deposit and transfer their tokens. However the permit functionality is unprotected and could be front-ran to DoS such deposits.

**Attack Scenario**\
The issue lies in the way ERC20 permits work - the ``permit`` function validates that the provided signature matches the owner/signer of the message, but it does not validate the executor of the ``permit``, meaning for e.g Alice can grant a permit for Bob, but Mike can call ``permit`` on behalf of Alice or Bob. This functionality is not problematic on it's own. However, when ``permit`` calls are a part of a transaction call chain, they can be front-ran and the transaction can be force reverted, since calling ``permit`` on a used signature will obviously fail.

In the context of the file:
1. Alice wants to grant Bob permission to deposit tokens on her behalf with several batched permits
2. Bob calls ``multiTokenDeposit()`` and provides the given permits, which internally calls `` _multiTokenTransferWithPermit``, which finally does ``permit2.permit(msg.sender, _permit, _signature)`` to execute the permit and finish the deposit

However, when Alice grants those permits to Bob and he tries to execute them, the signature's details are exposed to the mempool.
A malicious user can:
1. See the permit signature parameters provided by Bob
2. Front-run his ``multiTokenDeposit()`` call and do a direct call to ``permit2.permit(address(Bob), _permit, _signature)`` and use up the signature.
3. Now Bob's attempt to deposit would fail, since the signature he provided is already used up and his allowance is grant, thus when he reaches ``permit2.permit(msg.sender, _permit, _signature)`` he will face a revert. 

The issue is 1 degree worse in the given context, due to the usage of batched permits. The malicious user who front-runs and DoSes the deposit can do so only for the last permit in the batch. This means that if we have 100 permits and he uses only the last one, he will force Bob to waste the gas for going over all 100 permits and revert on the last one.

You can read-up on the problem here also: https://www.trust-security.xyz/post/permission-denied

**Attachments**

1. **Proof of Concept (PoC) File**
<!-- You must provide a file containing a proof of concept (PoC) that demonstrates the vulnerability you have discovered. -->

2. **Revised Code File (Optional)**
<!-- If possible, please provide a second file containing the revised code that offers a potential fix for the vulnerability. This file should include the following information:
- Comment with a clear explanation of the proposed fix.
- The revised code with your suggested changes.
- Any additional comments or explanations that clarify how the fix addresses the vulnerability. -->

**Recommendation**\

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Velvet-Capital-0x0bb0c08fd9eeaf190064f4c66f11d18182961f77/issues/5_
