# [H] Possible Signature Malleability in OpenZeppelin ECDSA

## Summary
Severity: High
Contest weight: 0.6372
Dataset id: 12615
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The OPLimitOrder contract relies on a number of library contracts to facilitate its functionality and organization. One specific one is the popular OpenZeppelin, which is an open-source framework to build secure smart contracts. It comes to our attention the imported @openzeppelin/contracts has the 4.7.0 version, which has a so-called ECDSA signature malleability issue on its signature verification logic.

To elaborate, we show below the affected function fillOpenOrder(), which is designed to fill an order order and makes use of SignatureChecker.isValidSignatureNow() to validate the given signature. Specifically, it checks whether a signature is valid for a given signer and data hash. If the signer is a smart contract, the signature is validated against that smart contract using ERC1271, otherwise it's validated using ECDSA.tryRecover().

```solidity
function fillOpenOrder(OpenOrder memory order, bytes calldata signature, uint256 fillingDeposit, bytes memory dexData) external override nonReentrant {
    require(block.timestamp <= order.deadline, EXR);
    bytes32 orderId = _openOrderId(order);
    uint256 remainingDeposit = _remaining[orderId];
    require(remainingDeposit != _ORDER_FILLED, "RD0");
    if (remainingDeposit == _ORDER_DOES_NOT_EXIST) {
        remainingDeposit = order.deposit;
    } else {
        remainingDeposit -= 1;
    }
    require(fillingDeposit <= remainingDeposit, FTB);
    require(SignatureChecker.isValidSignatureNow(order.owner, _hashOpenOrder(order), signature), "SNE");
}

function isValidSignatureNow(address signer, bytes32 hash, bytes memory signature) internal view returns (bool) {
    (address recovered, ECDSA.RecoverError error) = ECDSA.tryRecover(hash, signature);
    if (error == ECDSA.RecoverError.NoError && recovered == signer) {
        return true;
    }
    (bool success, bytes memory result) = signer.staticcall(
        abi.encodeWithSelector(IERC1271.isValidSignature.selector, hash, signature)
    );
    return (success && result.length == 32 && abi.decode(result, (bytes4)) == IERC1271.isValidSignature.selector);
}
```

However, the current version of tryRecover() is vulnerable to a kind of signature malleability due to accepting EIP-2098 compact signatures in addition to the traditional 65 byte signature format. Note that this is only an issue for the functions that take a single bytes argument, and not the functions that take r, v, s or r, vs as separate arguments.

## Recommendation
Upgrade imported library of @openzeppelin/contracts to the latest version (>=4.7.3) to resolve the possible signature malleability issue.
