# [M] Wrong DOMAIN_SEPARATOR

## Summary
Severity: Medium
Contest weight: 0.4175
Dataset id: 7537
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability originates from an incorrect calculation of the EIP‑712 DOMAIN_SEPARATOR within the BathToken contract. During contract initialization the code builds the DOMAIN_SEPARATOR by hashing the contract name together with other domain fields, but the contract name variable is assigned only after the hash operation. Because the name used in the hash is still the default zero value at that moment, the resulting DOMAIN_SEPARATOR does not reflect the actual token name that will later appear on‑chain. This ordering flaw belongs to a class of initialization‑order bugs where state variables required for cryptographic domain construction are set in the wrong sequence. The impact is that any functionality that relies on the DOMAIN_SEPARATOR—most notably EIP‑2612 permit signatures, meta‑transactions, or off‑chain signed approvals—will fail verification, as signed messages will be validated against a mismatched domain. From a user’s perspective, attempts to approve a token via a signed permit will revert with an "invalid signature" error, leading to a perception that the token is broken or that approvals are silently ignored. The issue manifests whenever the initialize function is called, which is typically during deployment of a new BathToken instance; any subsequent calls that depend on the domain separator inherit the wrong value. It was discovered during a systematic audit of the contract’s initialization logic, where the auditor noted that the name assignment occurs after the DOMAIN_SEPARATOR computation. The bug can be subtle because the contract will still compile and appear functional; only signature‑based interactions expose the fault, making it easy to overlook during manual testing. To remediate the issue, the contract should set the name (or any other domain‑relevant fields) before computing the DOMAIN_SEPARATOR, ensuring the hash incorporates the correct values. In broader terms, developers should verify that all inputs to a domain‑separator hash are fully initialized prior to the hash operation, adhering to the EIP‑712 specification and preventing mismatched signatures that break token approval flows.

## Proof of Concept
In the `initialize` method of the `BathToken` contract, the `name` of the contract is used to calculate the `DOMAIN_SEPARATOR`, however said name is set later, so it will use an incorrect `name`, making it impossible to calculate the `DOMAIN_SEPARATOR` correctly.

```solidity
DOMAIN_SEPARATOR = keccak256(
    abi.encode(
        keccak256(
            "EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)"
        ),
        keccak256(bytes(name)),
        keccak256(bytes("1")),
        chainId,
        address(this)
    )
);
name = string(abi.encodePacked(_symbol, (" v1")));
```

Affected source code:

  * [BathToken.sol#L199-L210](https://github.com/code-423n4/2022-05-rubicon/blob/521d50b22b41b1f52ff9a67ea68ed8012c618da9/contracts/rubiconPools/BathToken.sol#L199-L210)

## Recommendation
* Set the `name` before using it.
