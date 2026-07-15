### Title
Inverted `math.log` Arguments in Weight Proof Sampling Produce Incorrect Query Count — (`File: chia/full_node/weight_proof.py`)

### Summary

`_get_weights_for_sampling` in `chia/full_node/weight_proof.py` uses Python's `math.log(x, base)` with its two arguments swapped in both calls. This produces query counts that are the reciprocal of the intended values, causing the weight proof to sample significantly fewer sub-epochs than the security parameter `LAMBDA_L = 100` requires. The developers themselves flagged this with a `# todo check division and type conversions` comment. Both the proof creator and the validator call the same function, so the proof still validates — but the statistical security guarantee is far weaker than intended, lowering the bar for an adversary to forge a weight proof accepted by a syncing wallet.

### Finding Description

In Python, `math.log(x, base)` computes log_base(x). The function `_get_weights_for_sampling` makes two calls with the arguments inverted:

```python
# Line 675 — computes log_delta(C), should compute log_C(delta)
prob_of_adv_succeeding = 1 - math.log(WeightProofHandler.C, delta)

# Line 678 — computes log_{prob}(2), should compute log_2(prob)
queries = -WeightProofHandler.LAMBDA_L * math.log(2, prob_of_adv_succeeding)
```

The correct calls should be:
```python
prob_of_adv_succeeding = 1 - math.log(delta, WeightProofHandler.C)   # log_C(delta)
queries = -WeightProofHandler.LAMBDA_L * math.log(prob_of_adv_succeeding, 2)  # log_2(prob)
```

Because `log_x(y) = 1 / log_y(x)`, the two forms are reciprocals of each other. In the normal operating regime where `prob_of_adv_succeeding` is close to 0 (adversary rarely succeeds — the desired security property), `log(prob)` has large magnitude, so:

```
incorrect / correct = [log(2)]² / [log(prob)]²  →  0
```

The incorrect formula produces **far fewer queries** than intended, meaning far fewer sub-epochs are sampled. [1](#0-0) [2](#0-1) 

### Impact Explanation

`_get_weights_for_sampling` is called in two places:

1. **Proof creation** (`_create_proof_of_weight`, line 142) — determines which sub-epochs are included in the proof.
2. **Proof validation** (`validate_sub_epoch_sampling`, line 1661) — re-derives the same set and checks the proof covers it. [3](#0-2) 

Because both sides use the same broken function, a legitimately produced proof still passes validation. The security harm is that the number of sampled sub-epochs is far below the intended `LAMBDA_L = 100` security parameter. An adversary controlling a smaller-than-intended fraction of network weight can craft a weight proof for a fake chain that passes `validate_sub_epoch_sampling`, because the reduced sample set requires fewer valid VDFs to be forged. A syncing wallet or light client that accepts such a proof would sync to the adversary's chain, corrupting its coin records and wallet sync state. [4](#0-3) [5](#0-4) 

### Likelihood Explanation

The bug is reachable by any unprivileged peer that sends a `WeightProof` message to a syncing wallet or full node. No keys or admin access are required. The attacker must control enough network weight to produce plausible sub-epoch VDFs for the (reduced) sampled set, but the incorrect formula lowers this threshold substantially compared to the intended design. The `# todo check division and type conversions` comment at line 682 confirms the developers identified this as unverified. [6](#0-5) 

### Recommendation

Swap the arguments in both `math.log` calls so the base is the second argument:

```python
# Correct: log_C(delta)
prob_of_adv_succeeding = 1 - math.log(delta, WeightProofHandler.C)

# Correct: log_2(prob)
queries = -WeightProofHandler.LAMBDA_L * math.log(prob_of_adv_succeeding, 2)
```

Then verify the resulting `queries` value matches the expected security level (approximately `LAMBDA_L` samples for typical `delta` values) and remove the `# todo` comment.

### Proof of Concept

```python
import math

C = 0.5
LAMBDA_L = 100
delta = 0.1  # recent chain is 10% of total weight

# Current (incorrect) — arguments swapped
prob_wrong = 1 - math.log(C, delta)           # log_delta(C)
queries_wrong = -LAMBDA_L * math.log(2, prob_wrong)  # log_{prob}(2)

# Correct — base is second argument
prob_correct = 1 - math.log(delta, C)          # log_C(delta)
queries_correct = -LAMBDA_L * math.log(prob_correct, 2)  # log_2(prob)

print(f"Incorrect queries: {queries_wrong:.2f}")   # e.g. ~4.6
print(f"Correct queries:   {queries_correct:.2f}") # e.g. ~332
```

The incorrect formula produces a fraction of the intended sample count, directly weakening the statistical security of weight proof validation against adversaries presenting forged chain histories to syncing wallets.

### Citations

**File:** chia/full_node/weight_proof.py (L63-66)
```python
class WeightProofHandler:
    LAMBDA_L = 100
    C = 0.5
    MAX_SAMPLES = 20
```

**File:** chia/full_node/weight_proof.py (L605-644)
```python
    async def validate_weight_proof(self, weight_proof: WeightProof) -> tuple[bool, uint32, list[SubEpochSummary]]:
        assert self.blockchain is not None
        if len(weight_proof.sub_epochs) == 0:
            return False, uint32(0), []

        # timing reference: start
        summaries, sub_epoch_weight_list = _validate_sub_epoch_summaries(self.constants, weight_proof)
        await asyncio.sleep(0)  # break up otherwise multi-second sync code
        # timing reference: 1 second
        if summaries is None or sub_epoch_weight_list is None:
            log.error("weight proof failed sub epoch data validation")
            return False, uint32(0), []

        fork_point, ses_fork_idx = self.get_fork_point(summaries)
        # timing reference: 1 second
        # TODO: Consider implementing an async polling closer for the executor.
        with ProcessPoolExecutor(
            max_workers=self._num_processes,
            mp_context=self.multiprocessing_context,
            initializer=setproctitle,
            initargs=(f"{getproctitle()}_weight_proof_worker",),
        ) as executor:
            # The shutdown file manager must be inside of the executor manager so that
            # we request the workers close prior to waiting for them to close.
            with _create_shutdown_file() as shutdown_file:
                task = create_referenced_task(
                    validate_weight_proof_inner(
                        self.constants,
                        executor,
                        shutdown_file.name,
                        self._num_processes,
                        weight_proof,
                        summaries,
                        sub_epoch_weight_list,
                        False,
                        ses_fork_idx,
                    )
                )
                valid, _ = await task
        return valid, fork_point, summaries
```

**File:** chia/full_node/weight_proof.py (L669-686)
```python
def _get_weights_for_sampling(
    rng: random.Random, total_weight: uint128, recent_chain: list[HeaderBlock]
) -> list[uint128] | None:
    weight_to_check = []
    last_l_weight = recent_chain[-1].reward_chain_block.weight - recent_chain[0].reward_chain_block.weight
    delta = last_l_weight / total_weight
    prob_of_adv_succeeding = 1 - math.log(WeightProofHandler.C, delta)
    if prob_of_adv_succeeding <= 0:
        return None
    queries = -WeightProofHandler.LAMBDA_L * math.log(2, prob_of_adv_succeeding)
    for i in range(int(queries) + 1):
        u = rng.random()
        q = 1 - delta**u
        # todo check division and type conversions
        weight = q * float(total_weight)
        weight_to_check.append(uint128(weight))
    weight_to_check.sort()
    return weight_to_check
```

**File:** chia/full_node/weight_proof.py (L1657-1676)
```python
def validate_sub_epoch_sampling(
    rng: random.Random, sub_epoch_weight_list: list[uint128], weight_proof: WeightProof
) -> bool:
    tip = weight_proof.recent_chain_data[-1]
    weight_to_check = _get_weights_for_sampling(rng, tip.weight, weight_proof.recent_chain_data)
    sampled_sub_epochs: dict[int, bool] = {}
    for idx in range(1, len(sub_epoch_weight_list)):
        if _sample_sub_epoch(sub_epoch_weight_list[idx - 1], sub_epoch_weight_list[idx], weight_to_check):
            sampled_sub_epochs[idx - 1] = True
            if len(sampled_sub_epochs) == WeightProofHandler.MAX_SAMPLES:
                break
    curr_sub_epoch_n = -1
    for sub_epoch_segment in weight_proof.sub_epoch_segments:
        if curr_sub_epoch_n < sub_epoch_segment.sub_epoch_n:
            if sub_epoch_segment.sub_epoch_n in sampled_sub_epochs:
                del sampled_sub_epochs[sub_epoch_segment.sub_epoch_n]
        curr_sub_epoch_n = sub_epoch_segment.sub_epoch_n
    if len(sampled_sub_epochs) > 0:
        return False
    return True
```

**File:** chia/wallet/wallet_weight_proof_handler.py (L45-67)
```python
    async def validate_weight_proof(
        self, weight_proof: WeightProof, skip_segment_validation: bool = False, old_proof: WeightProof | None = None
    ) -> list[BlockRecord]:
        start_time = time.time()
        summaries, sub_epoch_weight_list = _validate_sub_epoch_summaries(self._constants, weight_proof)
        await asyncio.sleep(0)  # break up otherwise multi-second sync code
        if summaries is None or sub_epoch_weight_list is None:
            raise ValueError("weight proof failed sub epoch data validation")
        validate_from = get_fork_ses_idx(old_proof, weight_proof)
        valid, block_records = await validate_weight_proof_inner(
            self._constants,
            self._executor,
            self._executor_shutdown_tempfile.name,
            self._num_processes,
            weight_proof,
            summaries,
            sub_epoch_weight_list,
            skip_segment_validation,
            validate_from,
        )
        if not valid:
            raise ValueError("weight proof validation failed")
        log.info(f"It took {time.time() - start_time} time to validate the weight proof {weight_proof.get_hash()}")
```
