# [C] Unchecked Allocation May Panic In PeginMeta::deserialization()

## Summary
Severity: Critical
Contest weight: 0.2932
Dataset id: 15105
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A memory exhaustion vulnerability exists when deserialising peg-in proofs. The memory exhaustion may crash the node, causing a chain halt. The function PeginMetaV0::deserialize() allocates a vector using Vec::with_capacity() based on a decoded value. As such, a malicious user may set the value large enough to exhaust all memory in the machine. ```rust
pub fn deserialize(mut bytes: &[u8]) -> Result<(Self, usize), PeginDataError> {
    // ... snipped
    block_headers: {
        let len = btcencode::VarInt::consensus_decode(&mut bytes)?.0; // @audit untrusted input
        let mut ret = Vec::with_capacity(len as usize); // @audit panic if len is larger than available memory
        for _ in 0..len {
            ret.push(Decodable::consensus_decode(&mut bytes)?);
        }
    }
    // ... snipped
}
```
The len is decoded based on untrusted input that anyone can send to the Minting.sol contract in the metadata bytes. An attacker may send maliciously crafted metadata bytes to the Minting.sol contract with the len set to a very high number (e.g. u64::MAX). The result would be allocating a vector of u64::MAX which causes an out of memory panic and crashes the node. The impact and likelihood are rated as high as arbitrary users may send a transaction to the Minting contract, mint() function to crash all nodes on the network.

## Recommendation
Check that the decoded length from the metadata bytes doesn't exceed a maximum value and fail the decoding if it exceeds the value.
