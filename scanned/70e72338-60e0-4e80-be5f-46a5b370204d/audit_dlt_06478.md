# [M] Attacker can consume victim `TransactionForwarder_v1` nonce, but force the tx to revert

## Summary
Severity: Medium
Chain: Smart contract
Component: Inverter-Network
Published: 2024-06-15
Source: https://github.com/hats-finance/Inverter-Network-0xe47e52c4fea05e555920f1dcdcc6fb8eca103eeb/issues/133
Type: hats-finding

## Details
**Github username:** @NicolaMirchev
**Twitter username:** EgisSec
**Submission hash (on-chain):** 0x16ce08867e437e61c8c693074c3a38529c95b2304b759a676a6f67254ea4c76c
**Severity:** medium

**Description:**
**Description**\
Protocol support [EIP2771](https://eips.ethereum.org/EIPS/eip-2771) with custom multicall implementation in [TransactionForwarder_v1](https://github.com/hats-finance/Inverter-Network-0xe47e52c4fea05e555920f1dcdcc6fb8eca103eeb/blob/09e3a91bdc298a8666f666efbce408178cd83ec8/src/external/forwarder/TransactionForwarder_v1.sol#L32-L35). Because of the way [OZ implements `executeBatch`](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/83c7e45092dac350b070c421cd2bf7105616cf1a/contracts/metatx/ERC2771Forwarder.sol#L163-L194), it is possible for a malicious party to use viticm's nonce, no matter if the corresponding tx succeeded, or not. Additionally, malicious party can perform in one transaction -> `1. anything possible on-chain -> 2.try to execute victim transaction (use the nonce) -> 3. anything possible on-chain`
By "anything possible on-chain" we can undestand withdrawing and paying flashloans, interacting with Inverter contracts to get them in state, where victim call would revert, etc.
This may not seem harmful, but if used on the right place, in the right time, it can be dangerous.
One such example is if signer has signed a transaction for buying X amount bonding tokens with Y minAmount of corresponding issuance tokens. Now when executer try to submit the transaction, expliter can front-run him, buying some issuance tokens to increase the price of the issuance tokens, call `TransactionForwarder_v1::executeBatch` with the victim's transaction and signature. The transaction will revert, because X (issuance token bought) amount would be < Y (min issuance token wanted). But the nonce for that signature would be used:
```
    function ERC2771Forwarder::_execute(
        ForwardRequestData calldata request,
        bool requireValidRequest
    ) internal virtual returns (bool success) {
        (bool isTrustedForwarder, bool active, bool signerMatch, address signer) = _validate(request);
...
        if (isTrustedForwarder && signerMatch && active) {
            // Nonce should be used before the call to prevent reusing by reentrancy
            uint256 currentNonce = _useNonce(signer);

            uint256 reqGas = request.gas;
            address to = request.to;
            uint256 value = request.value;
            bytes memory data = abi.encodePacked(request.data, request.from);

            uint256 gasLeft;

            assembly {
                success := call(reqGas, to, value, add(data, 0x20), mload(data), 0, 0)
                gasLeft := gas()
            }

            _checkForwardedGas(gasLeft, request);

            emit ExecutedForwardRequest(signer, currentNonce, success);
        }
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Inverter-Network-0xe47e52c4fea05e555920f1dcdcc6fb8eca103eeb/issues/133_
