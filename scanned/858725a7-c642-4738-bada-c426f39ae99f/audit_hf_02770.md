# [H] change_output Validation Can Be Bypassed

## Summary
Severity: High
Contest weight: 0.3445
Dataset id: 15148
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A malicious coordinator can bypass the validation checks on the change_output to send the change to their own address.
When a psbt is received by a peer during the signing process validate_outputs() is called to ensure the psbt only contains legitimate peg-out transactions. Additionally, the change_output is also validated to ensure that any change from the inputs is sent to the aggregated public key. However, this validation only checks if one of the outputs is sent to the aggregated public key. It does not check that this output is the change output. As such, a malicious coordinator could create a peg-out that is sent to the aggregated public key and include it in the psbt. This will result in the validation passing regardless of the actual destination of the change_output, allowing the coordinator to steal the change.
bin/btc-server/src/util.rs
```rust
if !change_outputs.is_empty() {
    // TxOut scriptpubkey should be scriptpubkey derived from aggregated public key
    let agg_pk = public_key_package.verifying_key().to_secp_pk().expect("valid secp pk");
    let expected_script_pubkey = generate_taproot_change_scriptpubkey(&agg_pk);
    // TODO remove the clone here
    let tx = psbt.clone().extract_tx_unchecked_fee_rate();
    let has_correct_change =
        tx.output.iter().any(|o| o.script_pubkey == expected_script_pubkey); // @audit only checks a single output is a expected address
    if !has_correct_change {
        return Err(ValidateOutputsError::InvalidChangeOutput);
    }
}
```
The impact is rated as high as the coordinator may drain the multisig account balance by extracting change from each UTXO. The likelihood is rated as medium as this attack vector is restricted to the coordinator.

## Recommendation
It is recommended to validate the specific change_output such that the script_pubkey is the aggregated public key.
