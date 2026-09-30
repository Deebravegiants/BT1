# [H] Lack Of Authentication Of Peers During DKG

## Summary
Severity: High
Contest weight: 0.2454
Dataset id: 15149
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When receiving a message during the distributed key generation (DKG) no authentication of the sender occurs. Rather, the value of frost_identifier is assumed to be the sender's identifier. However, frost_identifier is part of the message and can be set arbitrarily by the sender. As such, a malicious peer may send dkg round packages while impersonating multiple other peers. This could eventually lead to the malicious peer obtaining enough shares of the key such that they own the entire multisig.
crates/consensus/authority/src/frost_task.rs
```rust
match peer_message {
    PeerMessageResponse::Dkg(dkg_response) => {
        let DkgResponse { response_type, identifier, data } = dkg_response;
        let frost_identifier = match deserialize_frost_peer_id(identifier) {
            Ok(frost_identifier) => frost_identifier,
            Err(e) => {
                error!(target: "consensus::authority::frost_task::start_task", "Error deserializing frost identifier in DKG payload");
                continue;
            }
        };
```

## Recommendation
Add an authentication mechanism using a peer's public key to ensure messages are matched to a peer.
