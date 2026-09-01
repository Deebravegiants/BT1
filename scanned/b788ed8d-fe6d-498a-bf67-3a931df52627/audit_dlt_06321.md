# [H] A malicious relayer(user) can intentionally call ``processPacket`` with insufficient gas to hit an OOG inside the try block

## Summary
Severity: High
Chain: Smart contract
Component: Catalyst-Exchange
Published: 2024-01-25
Source: https://github.com/hats-finance/Catalyst-Exchange-0x3026c1ea29bf1280f99b41934b2cb65d053c9db4/issues/43
Type: hats-finding

## Details
**Github username:** @PlamenTSV
**Twitter username:** @p_tsanev
**Submission hash (on-chain):** 0xad23046a1aa24982ef062cb55257147badaefc10b3cd208a2956c8a0e28120a1
**Severity:** high

**Description:**
**Description**\
The ``processPacket`` function of the IncentivizedMessageEscrow is supoosed to be called by off-chain agents(relayers), thus anybody can choose to relay the message. The protocol's current concerns are the ability of the feeRecipient to receive tokens, but this is a known effect.
Another previously reported issue mentions the need for a gas check when receiving an aknowledgement on the source and was fixed by adding an after-check for the gas.
A similiar issue could be replicated by a malicious relayer, but when receiving a message. 

**Attack Scenario**\
The current flow is ``processPacket``(with SRC_TO_DEST) -> ``_handleMessage`` -> ``_sendPacket``.
The last function ``sendPacket`` has it's sufficient gas check (per the comments) and the ``_handleMessage`` implements the fix from the previous audit. However, they use a try-catch block on it's receive message external call, with the intention of catching decoding(or any errors). Try-catch blocks in solidity are known to be tricky, the main reason here being that the catch block would not catch an out of gas error in the try statement.
This kind of uncaught revert would lead to 2 things:
1. Revert string would not be caught
2. An acknowledgement would not be sent to the source, meaning any escrowed assets would remain stuck(the call to ``onSendAssetFailure`` cannot occur).
Since anybody can choose to relay such a message, the sender is at risk of his message never succeeding nor giving out an acknowledement to the source, thus locking his funds into the escrow.

**Attachments**

1. **Proof of Concept (PoC) File**
<!-- You must provide a file containing a proof of concept (PoC) that demonstrates the vulnerability you have discovered. -->

2. **Revised Code File (Optional)**
<!-- If possible, please provide a second file containing the revised code that offers a potential fix for the vulnerability. This file should include the following information:
- Comment with a clear explanation of the proposed fix.
- The revised code with your suggested changes.
- Any additional comments or explanations that clarify how the fix addresses the vulnerability. -->

As far as I understood, there were assumptions for the previous audit's fix and it was to add the after-check, which does not suffice here due to the try-catch block being the core issue. I would advice for this case to do the gas check BEFORE the try-catch. The ``processPacket`` already creates a ``gasLimit`` variable reflecting the initial gas sent to the function.
