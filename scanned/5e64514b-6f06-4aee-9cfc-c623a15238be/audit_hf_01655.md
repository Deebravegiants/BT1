# [M] Wrong `DOMAIN_TYPEHASH` definition

## Summary
Severity: Medium
Contest weight: 0.4153
Dataset id: 8963
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability originates from an incorrect definition of the EIP‑712 domain type hash (DOMAIN_TYPEHASH) in the VotingEscrow contract. According to EIP‑712, the domain separator must be built from the exact struct definition, which includes the fields "name", "version", "chainId" and "verifyingContract". The contract, however, hard‑codes DOMAIN_TYPEHASH as the keccak256 hash of a struct that omits the required "string version" field. The delegateBySig function, which enables off‑chain signature based delegation, constructs the domain separator using the correct struct that includes the version field, but it then hashes that separator with the mismatched DOMAIN_TYPEHASH constant. Because the hash does not correspond to the actual struct, the recovered signer address does not match the expected signer, causing the function to revert with the message "VotingEscrow::delegateBySig: invalid signature". This mismatch can be exploited simply by attempting to submit any valid EIP‑712 signature to delegateBySig; the contract will reject it regardless of the signer’s intent, effectively breaking the delegation workflow. The impact is that legitimate users, dApps, or backend services that rely on signature‑based delegation cannot perform the action, leading to failed transactions and a user‑visible error. The issue manifests only when the delegateBySig function is invoked – normal token transfers and other operations remain unaffected. Affected parties include token holders who wish to delegate voting power, front‑end applications that offer signature delegation, and any integrators that assume compliance with EIP‑712. The bug was discovered during a manual audit when the auditor compared the on‑chain DOMAIN_TYPEHASH constant with the EIP‑712 specification and noticed the missing version field. The problem is subtle because the contract compiles without errors and the mismatch does not surface until a signature is processed, making it easy to overlook in standard testing. To remediate the issue, the constant should be redefined to include the version field—i.e., set DOMAIN_TYPEHASH to keccak256("EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)")—and any dependent code should be updated to use this corrected hash. Aligning the type hash with the EIP‑712 domain definition restores proper signature verification, allowing delegateBySig to function as intended and preserving the expected delegation behavior.

## Proof of Concept
In the build of the `DOMAIN TYPEHASH` the `string version` is forgotten, but the `delegateBySig` function, build the `domainSeparator` with the `string version`.

Some contract or dapp/backend could building the `DOMAIN_TYPEHASH` with "rigth" struct(include the `version`) and try to use the `delegateBySig` function but this function will revert in the L1378 with the message "VotingEscrow::delegateBySig: invalid signature" because the expect `DOMAIN_TYPEHASH` in the `VotingEscrow.sol` contract was built with the "wrong" struct.

## Recommendation
Acording the [EIP 712](https://eips.ethereum.org/EIPS/eip-712), in the [Definition of domainSeparator](https://github.com/ethereum/EIPs/blob/master/EIPS/eip-712.md#definition-of-domainseparator):

* "string version" the current major version of the signing domain. Signatures from different versions are not compatible

Add `string version`, to the `EIP712Domain` string, [L1106](https://github.com/code-423n4/2022-05-velodrome/blob/7fda97c570b758bbfa7dd6724a336c43d4041740/contracts/contracts/VotingEscrow.sol#L1106):

```solidity
bytes32 public constant DOMAIN_TYPEHASH = keccak256("EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)");
```
