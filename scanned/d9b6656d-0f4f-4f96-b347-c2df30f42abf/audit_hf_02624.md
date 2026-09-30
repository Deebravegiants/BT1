# [H] Skipped Slots Cause Relayer to Stall

## Summary
Severity: High
Contest weight: 0.3403
Dataset id: 14178
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The NEAR eth2-client may accept an attested execution header into unfinalized_headers, which the beacon chain later re-orgs into a skipped slot.
In such cases, the eth2_to_near_relay function block_known_on_near(slot) returns an Error while processing query data. This error is not handled, but is instead propagated by the calling function get_last_slot(), which is searching for the last beacon chain slot submitted to unfinalized_headers in order to submit a batch of headers up to the current unﬁnalised head. An inability to discover the last unﬁnalised beacon slot submitted will cause the eth2_to_near_relay to stall until the ﬁnalised slot on NEAR is larger than the last submitted slot.
The root cause of the error is due to the following chain of queries.
1. get_last_slot() attempts to ﬁnd the last non-skipped unﬁnalised slot submitted to the NEAR eth2-client.
2. Within, last_submitted_slot = self.eth_client_contract.get_last_submitted_slot() returns the skipped slot.
3. Until the skipped slot becomes ﬁnalised on the beacon chain, let slot = max(finalized_slot, last_submitted_slot); also returns the skipped slot.
4. In either linear or binary search options, the conditional statement self.block_known_on_near(slot)? will be reached.
5. self.block_known_on_near(slot)? queries get_beacon_block_body_for_block_id(&format!("{}", slot)) with the skipped slot, which returns an Error.
6. This Error case is not handled, and causes block_known_on_near(slot)? to fail.
7. This Error case is not handled in the calling function get_last_slot(), causing it to fail also.

## Recommendation
This issue can be mitigated by handling the error case for skipped slots in self.block_known_on_near(slot). Rather than propagating the error, allow get_last_slot() to search for the correct last submitted block.
Additionally, only submitting ﬁnalised execution headers on-chain mitigates this issue. Only submitting ﬁnalised blocks will prevent last_submitted_slot from becoming a skip slot.
