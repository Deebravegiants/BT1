# [M] Same second orders will fail given a timestamp nonce usage

## Summary
Severity: Medium
Contest weight: 0.5553
Dataset id: 6227
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The nonce for orders is calculated using both the timestamp and the address of the msg.sender:
```solidity
function orderMemoryData(bytes memory input) public payable isOn returns (bytes32) {
    uint32 nonce = uint32(block.timestamp);
    bytes32 id = generateId(msg.sender, nonce);
}
```
Nonces should not be based on timestamp, they should be their own variable that it is incremented by 1 every time the function gets called. If called twice during the same second, in this case, it would revert inside storeRemoteOrderPayload:
```solidity
require(
    escrowGMP.storeRemoteOrderPayload(id, keccak256(abi.encode(rewardAsset, maxReward, block.timestamp))),
    "RO#0"
);
```
Notice how even if it would go through there would be no distinction in the event emission, as no real nonce is used here, and the same event would be emitted:
```solidity
emit RemoteOrderCreated(id, nonce, msg.sender, block.timestamp);
```

## Recommendation
A nonce should be used as an incrementable variable each time a user calls that function, not based on timestamp.
