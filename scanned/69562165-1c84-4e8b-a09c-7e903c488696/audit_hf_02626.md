# [M] Unbounded State Growth of NEAR eth2-client

## Summary
Severity: Medium
Contest weight: 0.2021
Dataset id: 14180
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
eth2-client processes blocks in three stages:
1. Unﬁnalised execution headers are added to unfinalized_headers map.
2. Once they are ﬁnalised, headers are moved from unfinalized_headers to finalized_execution_blocks by tracing their ancestry up to the current ﬁnalised head of the beacon. The function only iterates over headers which are ﬁnalised, non-canonical headers remain as stale data.
3. Blocks are pruned from finalized_execution_blocks after a conﬁgurable period elapses (i.e. 7 days) and forgotten by the NEAR eth2-client.
Detailed in RBE2-02, eth2_to_near_relay is highly likely to submit headers which become stale data in unfinalized_headers during its routine operation, until it becomes non-functional.
There is no method to remove stale data from unfinalized_headers in the NEAR eth2-client, so this process implies that the state of the contract can grow indeﬁnitely. Although there are practical limits enforced by the relayer submission quota max_submitted_blocks_by_account parameter of eth2-client, a new relayer must be added when the former reaches its submission quota in order for the bridge to remain operational. Therefore, this process may continue with unbounded state growth, or halt the operation of the bridge.
Furthermore, because unregister_submitter() requires a relayer to have zero pending submissions in unfinalized_headers, a relayer who submits a single non-canonical block will never be able to unregister and recover their storage deposit.

## Recommendation
One way to mitigate this issue would be to allow stale headers to be pruned from unfinalized_headers in the NEAR eth2-client contract if they have a block number lower than the current ﬁnalised block.
