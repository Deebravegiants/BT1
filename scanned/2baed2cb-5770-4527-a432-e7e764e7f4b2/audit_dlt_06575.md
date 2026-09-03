# [M] A malicious/ inactive relayer of VaultBitcoinWallet can make withdrawal mechanism stuck forever

## Summary
Severity: Medium
Chain: Smart contract
Component: illuminex
Published: 2024-07-11
Source: https://github.com/hats-finance/illuminex-0x0bb4aa1f58719707405c231fcdf0b405714799cf/issues/84
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0xb06ad5822293a8d320d028d2c1e10cb09b042bd865af27b3bcd9fc546d8be8f3
**Severity:** medium

**Description:**
**Description**\
The `startOutgoingTxSerializing` function is called by a relayer of the `VaultBitcoinWallet` contract to start the process of withdrawal for pending withdrawals from the queue. This function deploys a new `TxSerializer` contract using the `TxSerializerFactory`. The owner of the `TxSerializer` contract is transferred to the `VaultBitcoinWallet`, which sets the relayer who called the `startOutgoingTxSerializing` function as the only relayer of the `TxSerializer`. This means ONLY the relayer who started the process can now interact with the TxSerializer, and make it reach a `Finished` seriailization state. So while the next step on the `VaultBitcoinWallet`, which is the `finaliseOutgoingTxSerializing`, can be called by any relayer, the `_sr.getRaw()` function call it makes will revert unless the original relayer makes the necessary calls to finalize the serialization. This means that in case the original relayer who called `startOutgoingTxSerializing` does not finilaze the serialization process, the withdrawal mechanism will remain stuck indefinetly, with no way to recovery - essentially giving an absolute power over the system to every individual relayer, requiring more trust in the relayers than what seems intended.

There also seems to be no reason for this excessive power to be granted to a single relayer, since either toggling more relayers, or (probably better) giving the ownership over the `TxSerializer` to the owner of the `VaultBitcoinWallet` could remove this power from the individual relayer.


**Attack Scenario**\
The above means that every single relayer has the power to stop the system's withdrawals indefinetly.

In case a relayer key is malicious or gets compromised, the attacker can disable withdrawals from the system, and demand a ransom to re-enable them.

In case an honest relayer who initiated the serialization process loses the key before the serialization process is finished (for example a hardware issue causes the key to be lost), the system's withdrawal mechanism will simply remain stuch forever, which no option to recover.


**Attachments**

1. **Proof of Concept (PoC) File**
The issue concerns the unnecessarily excessive power given to a single relayer account, not an external attack.

2. **Revised Code File (Optional)**

Add this as line 287 of `VaultBitcoinWallet.sol`: `_sr.transferOwner(owner());` 

<!-- If possible, please provide a second file containing the revised code that offers a potential fix for the vulnerability. This file should include the following information:
- Comment with a clear explanation of the proposed fix.
- The revised code with your suggested changes.
- Any additional comments or explanations that clarify how the fix addresses the vulnerability. -->
