# [H] New users can'tbe registered after slashing contrary to documentation

## Summary
Severity: High
Contest weight: 1.0000
Dataset id: 23347
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
RLN.sol has variable `SET_SIZE`, which defines maximum number of registered users. During slashing, users are deleted from registry:

```solidity
function slash(bytes32 privateKey, address rewardRecipient) private onlyRole(SLASHER_ROLE) {
    // Hash the private key using Poseidon to get identityCommitment
    uint256 identityCommitment = poseidonHasher.hash(uint256(privateKey));
    User memory member = members[identityCommitment];
    if (member.userAddress == address(0)) {
        revert RLN__MemberNotFound();
    }
    karma.slash(member.userAddress, rewardRecipient);
    @> delete members[identityCommitment];
}
```

According to documentation https://github.com/status-im/status-network-monorepo/blob/develop/status-network-contracts/docs/rln.md#registry-capacity:

> Once the registry reaches capacity, new registrations are rejected until space is available. When accounts are slashed, their identity commitments are removed from the registry, freeing up space for new registrations.

However slashing accounts doesn't free up space for new registrations:

```solidity
function register(uint256 identityCommitment, address user) external onlyRole(REGISTER_ROLE) {
    @> uint256 index = identityCommitmentIndex;
    @> if (index >= SET_SIZE) {
        revert RLN__SetIsFull();
    }
    if (members[identityCommitment].userAddress != address(0)) {
        revert RLN__IdCommitmentAlreadyRegistered();
    }
    /// forge-lint: disable-next-line(named-struct-fields)
    members[identityCommitment] = User(user, index);
    emit MemberRegistered(identityCommitment, index);
    unchecked {
        @> identityCommitmentIndex = index + 1;
    }
}
```

Impact: New users can't be registered after slashing contrary to documentation.

## Proof of Concept
```solidity
function slash(bytes32 privateKey, address rewardRecipient) private onlyRole(SLASHER_ROLE) {
    // Hash the private key using Poseidon to get identityCommitment
    uint256 identityCommitment = poseidonHasher.hash(uint256(privateKey));
    User memory member = members[identityCommitment];
    if (member.userAddress == address(0)) {
        revert RLN__MemberNotFound();
    }
    karma.slash(member.userAddress, rewardRecipient);
    @> delete members[identityCommitment];
}
```

```solidity
function register(uint256 identityCommitment, address user) external onlyRole(REGISTER_ROLE) {
    @> uint256 index = identityCommitmentIndex;
    @> if (index >= SET_SIZE) {
        revert RLN__SetIsFull();
    }
    if (members[identityCommitment].userAddress != address(0)) {
        revert RLN__IdCommitmentAlreadyRegistered();
    }
    /// forge-lint: disable-next-line(named-struct-fields)
    members[identityCommitment] = User(user, index);
    emit MemberRegistered(identityCommitment, index);
    unchecked {
        @> identityCommitmentIndex = index + 1;
    }
}
```

## Recommendation
Add missing feature or update documentation.
