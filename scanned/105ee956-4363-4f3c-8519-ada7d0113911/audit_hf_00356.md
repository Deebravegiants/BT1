# [H] Attacker can freeze chain and

## Summary
Severity: High
Contest weight: 0.6362
Dataset id: 1728
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Because the prevStateRoot is not validated until a batch is finalized, a committed batch with a malicious prevStateRoot can be used to both (a) win challenges against honest challengers and (b) halt the chain since it will be approved but be unable to be finalized. In Rollup.sol, if a malicious batch is proposed, the assumption is that the sequencer who proposed it will lose the challenge, get slashed, and the chain will be reset. These economic incentives prevent the chain from being regularly halted. This is based on the assumption that a sequencer can only win challenges if the batch they proposed is valid. However, the check that prevStateRoot is actually the postStateRoot of the previous batch only happens in `finalizeBatch()`. This check is sufficient to prevent batches with fake prevStateRoots from being finalized, but it does not stop these batches from being committed. This allows a malicious sequencer to propose any batch that performs a valid state transaction from a fake prevStateRoot. In most cases, a challenger will attack this invalid batch. However, it is possible for the sequencer to provide a valid proof of this state transition to steal the honest challenger's deposit and win the challenge. In the case that this happens, or that no challenge is performed, the committed batch will not be able to be finalized due to the following check:

```solidity
require(
    finalizedStateRoots[_batchIndex - 1] == BatchHeaderCodecV0.getPrevStateHash(memPtr),
    "incorrect previous state root"
);
```

This will freeze the chain and not allow any new batches to be finalized, since batches are committed sequentially and must be finalized sequentially.

Internal Preconditions
None

External Preconditions
None

Attack Path
1. Attacker proposes a batch that contains a valid state transition from a fake prevStateRoot.
2. If an honest challenger challenges the batch, the attacker provides a valid proof of the state transition to win the challenge and steal the challenger's deposit.
3. Whether or not the above happens, the chain is now halted, as the attacker's batch cannot be finalized, and no other batches can be finalized without it being finalized first.
4. The attacker will not be slashed, due to the fact that they won the challenge.
• An honest challenge will lose their deposit when a dishonest sequencer beats them in a challenge.
• No new batches will be able to be finalized, so the chain will halt and have to be manually rolled back by the admins.

## Recommendation
Check in `commitBatch()` that prevStateRoot is equal to the parentBatchHeader.postStateRoot.
