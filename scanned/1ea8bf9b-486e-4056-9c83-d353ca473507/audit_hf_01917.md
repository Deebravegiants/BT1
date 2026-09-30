# [C] The verifyUser method is flawed and it will not work Molly_report.md

## Summary
Severity: Critical
Contest weight: 0.4031
Dataset id: 10532
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
There are several problems with the verifyUser function:
```solidity
function verifyUser(bytes memory _data, bytes memory _signature)
external {
    bytes32 _hash = ECDSA.toEthSignedMessageHash(keccak256(_data));
    require(
        ECDSA.recover(_hash, _signature) == signer,
        "Invalid signature"
    );
    isVerified[msg.sender] = true;
```
- The first is the use of ECDSA.verify method to validate the signature.
```solidity
require(
    ECDSA.recover(_hash, _signature) == signer,
    "Invalid signature"
);
```
to change it. The signer is set in the constructor by calling the internal _setSigner function and there is
no way to call it again and change it to another signer:
```solidity
constructor() ERC20("Molly", "MOLY") {
```
This will lead to the require statement always reverting and returning "Invalid signature".
- The second problem is that even if the above problem is fixed, anyone can front run the call with the
same input parameters and be verified. For example, user Bob calls the function with valid bytes
memory _data, bytes memory _signature parameters which will pass the require statement
and he will become verified. However, while the call is in the mempool, malicious user Alice sees the
transaction and calls the function with the same input parameters as Bob but with higher gas price.
This will result in Alice being a verified user even if she is not supposed to be.
- The third problem is that the function calls the ECDSA.toEthSignedMessageHash method.
However, in the latest OpenZeppelin version of the libraries, the toEthSignedMessageHash
method is part of the MessageHashUtils library which should be imported as well, as it is best
security practice to use the latest versions of OZ libraries as they are constantly updated and
optimized.

## Recommendation
Consider comparing the ECDSA.recover signature to a valid signer. Also, include the msg.sender or
nonce as part of the validation as this will make the validation specific for each user. Finally, update the OZ
libraries to the latest version and import the above-mentioned library.
