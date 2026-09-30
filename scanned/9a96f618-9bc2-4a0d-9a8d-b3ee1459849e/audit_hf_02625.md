# [M] Relayer Will Submit Potentially Stale Blocks Until Submission Limit Is Reached

## Summary
Severity: Medium
Contest weight: 0.2199
Dataset id: 14179
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
eth2_to_near_relay submits the head of the beacon chain from the most recently attested (unﬁnalised) slot to the NEAR eth2-client, which gets registered in unfinalized_headers. Limits are set on the number of unﬁnalised submissions from each account to prevent unbounded state growth.
Each submission has the potential to be excluded from the ﬁnalised beacon chain in the case of a re-org. The relayer will therefore reach its unﬁnalised block submission quota through its routine operation. No longer will the account be able to submit new blocks or unregister as a submitter to receive its storage deposit refund. If only one relayer is connected to eth2-client, then the Eth2Near side of bridge operation will be stalled until a new relayer can be connected.
One cause of a beacon chain re-org is when the head of beacon chain is proposed late, after other validators have already attested to a skip slot. The next proposer will fork the late block (current head) and will create a new head which does not include the late block.
The code which determines which blocks to submit occur in the main run() loop. The following code selects the highest beacon slot by fetching the slot number of the current head through get_last_slot_number(). Each block between the last ﬁnalised block on NEAR and the beacon head will then be submitted on-chain.
let last_eth2_slot_on_eth_chain: u64 =
match self.beacon_rpc_client.get_last_slot_number() {
Ok(slot) => slot.as_u64(),
Err(err) => {
warn!(target: "relay", "Fail to get last slot on Eth. Error: {}", err);
continue;

## Recommendation
eth2_to_near_relay can be updated to only submit ﬁnalised execution headers to the NEAR eth2-client.
A re-org of a ﬁnalised block breaks the underlying assumptions of the Ethereum consensus. By applying the assumption that ﬁnalised blocks will not be re-orged, the number of blocks submitted by the relayer will be exactly the number of blocks between the current and previous ﬁnalised blocks. Hence, it will remain safely within its submission quota.
