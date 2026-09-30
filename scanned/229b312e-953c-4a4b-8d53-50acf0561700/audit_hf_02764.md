# [M] Increased Resource Usage By Not Disconnecting Non Federation Peers

## Summary
Severity: Medium
Contest weight: 0.1399
Dataset id: 15138
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the frost networking subprotocol, when a connection is received from a non-federation peer, the request is ignored in on_network_event::FrostProtocolEvent::ConnectionEstablished.
crates/net/network/src/frost/manager.rs
```rust
if !self.is_authority_peer(&peer_id) {
    return;
}
```
The on_network_event() function is triggered from polling the FrostProtoConnection stream. After sending the FrostProtocolEvent::ConnectionEstablished to the frost manager, the stream goes into RegistrationState::Pending state and awaits for a message on callback_rx receiver from the FrostManager.
However, since the manager returns immediately and does not explicitly disconnect from a non-authority peer, an unauthorised peer will be stuck in the Pending registration state and never resolve. An attacker may generate numerous of peer IDs and initiate connections to a federation peer. Each connection attempt consumes additional resources posing a minor DoS risk.

## Recommendation
Explicitly disconnect from non authorised peers by dropping the FrostConnection.
