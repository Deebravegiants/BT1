# [M] Strategist nonce is not checked

## Summary
Severity: Medium
Contest weight: 0.4591
Dataset id: 17731
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Strategist nonce is not checked while checking commitment. This makes impossible for strategist to cancel signed commitment. VaultImplementation.commitToLien is created to give the ability to borrow from the vault. The conditions of loan are discussed off chain and owner or delegate of the vault then creates and signes deal details. Later borrower can provide it as IAstariaRouter.Commitment calldata params param to VaultImplementation.commitToLien. After the checking of signer of commitment VaultImplementation._validateCommitment function calls AstariaRouter.validateCommitment.
```solidity
function validateCommitment(IAstariaRouter.Commitment calldata commitment)
    public
    returns (bool valid, IAstariaRouter.LienDetails memory ld)
{
    require(
        commitment.lienRequest.strategy.deadline >= block.timestamp,
        "deadline passed"
    );
    require(
        strategyValidators[commitment.lienRequest.nlrType] != address(0),
        "invalid strategy type"
    );
    bytes32 leaf;
    (leaf, ld) = IStrategyValidator(
        strategyValidators[commitment.lienRequest.nlrType]
    ).validateAndParse(
        commitment.lienRequest,
        COLLATERAL_TOKEN.ownerOf(
            commitment.tokenContract.computeId(commitment.tokenId)
        ),
        commitment.tokenContract,
        commitment.tokenId
    );
    return (
        MerkleProof.verifyCalldata(
            commitment.lienRequest.merkle.proof,
            commitment.lienRequest.merkle.root,
            leaf
        ),
        ld
    );
}
```
This function check additional params, one of which is commitment.lienRequest.strategy.deadline. But it doesn't check for the nonce of strategist here. But this nonce is used while signing. Also AstariaRouter gives ability to increment nonce for strategist, but it is never called. That means that currently strategist use always same nonce and can't cancel his commitment. Strategist can't cancel his commitment. User can use this commitment to borrow up to 5 times.

## Recommendation
Give ability to strategist to call increaseNonce function.
