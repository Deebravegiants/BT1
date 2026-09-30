# [H] Document Signature Bypass

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23494
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Buyers can pledge fortokens without having signed all documents that are required to be signed.

When buyers pledge() during the pledgeRound, it is verified that they have signed all the documents that are required to be signed. If at least one document is not signed, instead of reverting the tx, the execution will verify a signature on behalf of the signer, and, if this signature is legit, the execution continues.

```solidity
function _verifyDocumentSignature(
    PledgeData calldata data,
    address signer
) internal {
    (bool res, ) = IRemoraRWAToken(propertyToken).hasSignedDocs(signer);
    if (!res)
        IRemoraRWAToken(propertyToken).verifySignature(
            signer,
            data.docHash,
            data.signature
        );
}
```

The problem is that this implementation allows buyers to bypass the requirement to have signed all the documents by signing only one. For example: There are 3 documents that need to be signed, and the user has not signed any of them. The user calls pledge() and provides the signature's data to sign 1 document. Here is what will happen:

`PropertyToken::hasSignedDocs()` will return false because the user has not signed any of the 3 documents

```solidity
function hasSignedDocs(address signer) public view returns (bool, bytes32) {
    ...
    for (uint256 i = 0; i < numDocs; ++i) {
        bytes32 docHash = $._docHashes[i];
        //@audit => If one document that needs signature is not signed, returns false
        if (
            $._documents[docHash].needSignature &&
            $._signatureRecords[signer][docHash] == 0
        ) return (false, docHash);
    }
    //@audit => returns true only if all documents that requires signature are signed
    return (true, 0x0);
}
```

`PropertyToken::verifySignature()` won't revert because it will sign one of the 3 documents

```solidity
function verifySignature(
    address signer,
    bytes32 docHash,
    bytes memory signature
) external returns (bool result) {
    ...
    if (signer.code.length == 0) {
        //signer is EOA
        (address returnedSigner, , ) = ECDSA.tryRecover(digest, signature);
        result = returnedSigner == signer;
    } else {
        //signer is SCA
        (bool success, bytes memory ret) = signer.staticcall(
            ...
        );
        result = (success && ret.length == 32 && bytes4(ret) == MAGICVALUE);
    }
    if (!result) revert InvalidSignature();
    if ($._signatureRecords[signer][docHash] == 0) {
        ...
    }
    //@audit => if the verification of the provided signature succeeds, execution continues
}
```

The execution will continue even though the user has only signed 1 of the 3 documents that have to be signed because `_verifyDocumentSignature()` will be bypassed to only enforce one signature, and, when transferring from the holderWallet to the signer, the `checkTC` is set as false.

```solidity
function pledge(PledgeData calldata data) external nonReentrant {
    ...
    _verifyDocumentSignature(data, signer);
    ...
    //@audit => checkTC is set as false
    //this address should be whitelisted in property token
    IRemoraRWAToken(propertyToken).adminTransferFrom(
        holderWallet,
        signer,
        numTokens,
        false, // <====> checkTC //
        true
    );
    ...
}
```

`adminTransferFrom` uses `checkTC` to verify terms and conditions:

```solidity
function adminTransferFrom(
    address from,
    address to,
    uint256 value,
    bool checkTC,
    bool enforceLock
) external restricted returns (bool) {
    ...
    //@audit => checkTC as false effectively bypass the verification of TC to be signed
    (bool res, ) = hasSignedDocs(to);
    if (checkTC && !res) revert TermsAndConditionsNotSigned(to);
    ...
}
```

Impact: Buyers can purchase tokens even though they have not signed all the documents that have to be signed.

## Recommendation
Revert the execution if the call to `PropertyToken.hasSignedDocs()` returns false.

```solidity
function _verifyDocumentSignature(
    PledgeData calldata data,
    address signer
) internal {
    (bool res, ) = IRemoraRWAToken(propertyToken).hasSignedDocs(signer);
    - if (!res)
    - IRemoraRWAToken(propertyToken).verifySignature(
    -     signer,
    -     data.docHash,
    -     data.signature
    - );
    + if (!res) revert NotAllDocumentsAreSigned();
}
```
