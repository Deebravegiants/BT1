# [M] Wrong block will be verified for snapshot

## Summary
Severity: Medium
Chain: Smart contract
Component: SafeStaking-by-HOPR
Published: 2023-10-13
Source: https://github.com/hats-finance/SafeStaking-by-HOPR-0x607386df18b663cf5ee9b879fbc1f32466ad5a85/issues/38
Type: hats-finding

## Details
**Github username:** --
**Submission hash (on-chain):** 0xac8c071250c3ad10c7d4cb1db6be15c7b400705f7450a1c23d97366783e3475d
**Severity:** medium

**Description:**
**Description**\

The issue of verification belongs to [Arbitrum](https://docs.arbitrum.io/time) and [Optimism]( https://community.optimism.io/docs/developers/build/differences/#) chain  as they have different pattern for block number as mentioned in thier documentation.

Accessing block number within a Arbitrum chain will return value synced to the L1 block number which the sequencer has received the transaction.

In Optimism the block.number is not a reliable source of time based information and the time between each block is also different from Mainnet.

This is because each transaction on Optimism is placed in a separate block and blocks are not produce at a constant rate. 




**Attack Scenario**\

Using block.number as a time measurement standard can lead to inaccurate verification of snapshot taken for a block.

The difference can grow significantly as the verification of snapshot will be attached to previous result using ```latestRoot.rootHash``` in L#104 of Ledger.sol.

**Attachments**
https://github.com/hoprnet/hoprnet/blob/master/packages/ethereum/contracts/src/Ledger.sol#L102

1. **Proof of Concept (PoC) File**

The indexEvent() function will not be able to detect and verify correct block in which snapshots were taken due to use of block.number that generate different result on different L2 chains.

```
    function indexEvent(bytes memory payload) internal {
        bool createSnapshot = false;
        if (block.timestamp > latestRoot.timestamp + snapshotInterval) {
            createSnapshot = true;
        }

```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/SafeStaking-by-HOPR-0x607386df18b663cf5ee9b879fbc1f32466ad5a85/issues/38_
