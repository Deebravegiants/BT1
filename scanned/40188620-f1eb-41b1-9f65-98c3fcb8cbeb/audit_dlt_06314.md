# [M] Signature Bypass when renounceOwnership() happens in IncentivizedMockEscrow.sol.

## Summary
Severity: Medium
Chain: Smart contract
Component: Catalyst-Exchange
Published: 2024-01-29
Source: https://github.com/hats-finance/Catalyst-Exchange-0x3026c1ea29bf1280f99b41934b2cb65d053c9db4/issues/60
Type: hats-finding

## Details
**Github username:** @erictee2802
**Twitter username:** 0xEricTee
**Submission hash (on-chain):** 0x9a7fc1c76d4ef9f3e4798e9fb4975f13b683a020457a9f74c185117188d1b386
**Severity:** medium

**Description:**
**Description**\
From `IncentivizedMockEscrow.sol`:
```javascript
contract IncentivizedMockEscrow is IncentivizedMessageEscrow, Ownable2Step {
```
The contract inherits `Ownable2Step` contract, meaning that `renounceOwnership()` function can be used to set owner to address(0).

In `IncentivizedMockEscrow::_verifyPacket()`:

```javascript
 function _verifyPacket(bytes calldata _metadata, bytes calldata _message) internal view override returns(bytes32 sourceIdentifier, bytes memory implementationIdentifier, bytes calldata message_) {

        // Get signature from message payload
        (uint8 v, bytes32 r, bytes32 s) = abi.decode(_metadata, (uint8, bytes32, bytes32));

        // Get signer of message
        address messageSigner = ecrecover(keccak256(_message), v, r, s); 

        // Check signer is the same as the stored signer.
        require(messageSigner == owner(), "!signer");

        // Load the identifier for the calling contract.
        implementationIdentifier = _message[0:32];

        // Local "supposedly" this chain identifier.
        bytes32 thisChainIdentifier = bytes32(_message[64:96]);

        // Check that the message is intended for this chain.
        require(thisChainIdentifier == UNIQUE_SOURCE_IDENTIFIER, "!Identifier");

        // Local the identifier for the source chain.
        sourceIdentifier = bytes32(_message[32:64]);
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Catalyst-Exchange-0x3026c1ea29bf1280f99b41934b2cb65d053c9db4/issues/60_
