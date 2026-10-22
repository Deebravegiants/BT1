# [H] Add _mirrorConnector to _sendMessage of BaseMultichain

## Summary
Severity: High
Contest weight: 0.5426
Dataset id: 6810
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
The function _sendMessage() of BaseMultichain sends the message to the address of the _amb.
This doesn't seem right as the first parameter is the target contract to interact with according to multichain cross-chain. This should probably be the _mirrorConnector.
function _sendMessage(address _amb, bytes memory _data) internal {
Multichain(_amb).anyCall(
_amb, // Same address on every chain, using AMB as it is immutable
...
);
}
```

## Recommendation
Doublecheck the conclusion and change the code to:
- function _sendMessage(address _amb, bytes memory _data) ... {
+ function _sendMessage(address _amb, address _mirrorConnector, bytes memory _data) ... {
Multichain(_amb).anyCall(
- _amb,
+ _mirrorConnector
...
);
}
