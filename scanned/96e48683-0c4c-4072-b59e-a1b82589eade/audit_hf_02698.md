# [C] Insufficient Signature Hashing For SGX addInstances()

## Summary
Severity: Critical
Contest weight: 0.6254
Dataset id: 14641
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A bug exists in one of the addInstances() functions which allows replacing a current SGX instance with any arbitrary
address. The address may be non-SGX and therefore can operate outside of the trusted execution environment.
There are two implementations of addInstances(), one restricted to onlyOwner and the other allows current SGX
instances to add multiple new SGX instances. To prevent side-channel attacks on ECDSA signing, each instance must
replace the private key and address each time it generates a signature.
In the code snippet below, it can be seen that newInstance is not included in the signedHash. There are no other
restrictions on the value of newInstance. It can therefore be arbitrarily set by msg.sender to a non-SGX address.
```solidity
function addInstances(
    uint256 id,
    address newInstance,
    address[] calldata extraInstances,
    bytes calldata signature
) external returns (uint256[] memory ids) {
    bytes32 signedHash = keccak256(abi.encode("ADD_INSTANCES", extraInstances));
    address oldInstance = ECDSA.recover(signedHash, signature);
    if (!_isInstanceValid(id, oldInstance)) revert SGX_INVALID_INSTANCE();
    _replaceInstance(id, oldInstance, newInstance); //@audit newInstance is not signed by the old instance
    ids = _addInstances(extraInstances);
}
```
The impact is high as a malicious instance can create an ADD_INSTANCES attestation signature for extra instances. The
malicious user then sets the newInstance parameter to an address where the private key is known. With the malicious
address they are able to sign forged SGX proofs which are accepted by verifyProof().

## Recommendation
To resolve this issue, include the value of newInstance within the signedHash.
Furthermore, it is recommended to include a domain separator with address(this) and block.chainid within signedHash
to prevent replay of signatures on other contracts or chains. This can be achieved through the use of EIP-712: Typed
structured data hashing and signing.
Additionally, domain separation should be added to the function verifyProof() to ensure signatures are not re-usable
between the functions addInstances() and verifyProof().
Taiko
