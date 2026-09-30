# [H] Pending Peg-Out Validation Incorrectly Accounts For Limits

## Summary
Severity: High
Contest weight: 0.3148
Dataset id: 15146
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When validating pegouts in validate_outputs(), the function checks that all pending_pegout_ids that are stored in the database are also present in psbt_pegout_ids.
bin/btc-server/src/util.rs
```rust
for pegout_id in pending_pegout_ids.iter() { // @audit validates all pending pegouts in the DB
    if !psbt_pegout_ids.contains(pegout_id) {
        return Err(ValidateOutputsError::MissingPsbtPegout(*pegout_id));
    }
}
```
However, when the psbt signing is initiated by the coordinator, the number of pegouts to be included in the psbt is limited by UPPER_PEGOUT_BOUND.
bin/btc-server/src/bin/main.rs
```rust
async fn get_psbt(
    &self,
    req: tonic::Request<()>,
) -> Result<Response<PsbtResponse>, tonic::Status> {
    //...snipped
    // Select up to `UPPER_PEGOUT_BOUND` pegouts, sorted by age in ascending
    // order. Respectively, the oldest pegouts come first.
    let pending_pegouts = self.db.coord_pending_pegouts(UPPER_PEGOUT_BOUND).to_status()?; // @audit only fetches UPPER_PEGOUT_BOUND peg-outs
    //...snipped
}
```
This allows for a scenario where an attacker could create many small peg-out requests in the minting contracts over multiple blocks in the Botanix chain such that the UPPER_PEGOUT_BOUND limit is reached. As a result, not all pending pegouts will be included in the psbt. As a result, validate_outputs() will fail for any newly generated psbt, causing a permanent DoS to the peg-out mechanism.
The likelihood is as high as it would allow any user to stall the peg-out process.

## Recommendation
Modify validate_outputs() such that it accounts for the UPPER_PEGOUT_BOUND limit.
