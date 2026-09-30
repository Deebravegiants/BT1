# [H] FrostProtoMessage::decode_message() May Panic On Malformed Inputs

## Summary
Severity: High
Contest weight: 0.3293
Dataset id: 15133
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The FrostProtoMessage::decode_message() function decodes messages sent by other trusted federation peers. The function assumes that the bytes sent by peers cannot be an invalid FrostProtoMessage message. The malicious peer may send invalid bytes that can crash all other nodes.
For instance, receiving the input 0x00 can immediately crash the node due to an out of bounds access.
crates/net/network/src/frost/messages.rs
```rust
pub fn decode_message(buf: &mut &[u8]) -> Option<FrostProtoMessage> {
    if buf.is_empty() {
        return None;
    }
    let id = buf[0];
    buf.advance(1);
    let message_type = match id {
        0x00 => FrostProtoMessageId::Round1Dkg,
        // ... snipped
    };
    let message = match message_type {
        // Other cases remain unchanged
        FrostProtoMessageId::Round1Dkg => {
            let id_len = buf[0] as usize; // @audit index out of bounds panic if buf.len() == 0
```
The panic occurs as buf is empty after being advanced and therefore has length zero.
There are numerous issues that may call a panic in this function, consider the following list:
• Unsafe indexing of the slice buf.
• Usage of unwrap() on UTF-8 string conversion and PeerID decoding.
• Calling the function PeerId::from_slice() with invalid length input.
The issue is rated as high severity as any panics will cause the node to crash. The likelihood is rated as medium as peer connected nodes may trigger this function with arbitrary data by sending messages on the Frost subnet.

## Recommendation
Remove all panics and instead return None. Consider the following recommendations.
• Instead of using unsafe indexing, use safe indexing methods on slices like get() that return an Option.
• Avoid using unwrap() and handle error cases.
Macbeth Review
• Avoid using functions which may panic on malformed input such as PeerId::from_slice() and use try_from() variants.
