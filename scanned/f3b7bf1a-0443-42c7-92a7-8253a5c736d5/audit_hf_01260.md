# [H] safeAddress not included in signatures

## Summary
Severity: High
Contest weight: 0.2823
Dataset id: 5773
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The validation of signatures doesn't take into account the safeAddress (except when checking the number of approvals). This means signatures from the same approvers who are also involved in other organizations/sub daos/safes, could be reused. As the nonces (e.g. packPayoutNonce() ) are stored in a different storage location, the nonces can be reused and thus the payment can be done again.
Combined with the issue "More tokens can be retrieved from a safe via frontrunning", this means ETH/Tokens can be stolen.
function executePayroll(...) ... {
    ...
    validateSignatures(safeAddress, roots, signatures);
    ...
    bytes32 leaf = encodeTransactionData(to[i],tokenAddress[i],amount[i],payoutNonce[i]);
    ...
    if (MerkleProof.verify(proof[i][j], roots[j], leaf)) {
        ++approvals;
    }
    if (approvals >= orgs[safeAddress].approvalsRequired && ... ) {
        ...
    }
    ...
}
function validateSignatures(...) ... {
    ...
    address signer = validatePayrollTxHashes(roots[i], signatures[i]);
    ...
}
function validatePayrollTxHashes(...) ... {
    bytes32 digest = ... abi.encode(PAYROLL_TX_TYPEHASH, rootHash) ...
    return digest.recover(signature);
}

## Recommendation
Include the safeAddress in the signatures, for example in the following way:
function validatePayrollTxHashes(...) ... {
    -
    bytes32 digest = ... abi.encode(PAYROLL_TX_TYPEHASH, rootHash) ...
    +
    bytes32 digest = ... abi.encode(PAYROLL_TX_TYPEHASH, safeAddress, rootHash) ...
    return digest.recover(signature);
}
