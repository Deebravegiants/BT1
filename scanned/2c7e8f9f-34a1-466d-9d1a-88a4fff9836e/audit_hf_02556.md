# [M] AnyoneCanCall executeMigration() Once migrationDestination Is Set

## Summary
Severity: Medium
Contest weight: 0.5929
Dataset id: 13703
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The current implementation allows anyone to execute the executeMigration() function once the migrationDestination is set, bypassing the intended logic of requiring a >50% vote based on capital. The function executeMigration() is used to mint the Portal NFT and prepare user stakes transfer to a new Adapter. The used checks inside are insufficient.

Attack Scenario

1. The owner set migrationDestination

2. executeMigration() is called

3. migrationTime equals 0, it is only set when this condition is true in the acceptMigrationDestination() function:

```solidity
if (votesForMigration > totalPrincipalStaked / 2 && migrationTime == 0) {
    migrationTime = block.timestamp + TIMELOCK;
}
```

so we pass that check:

```solidity
// @dev Ensure that the timelock has passed
if (block.timestamp < migrationTime && migrationTime > 0) {
    revert ErrorsLib.isTimeLocked();
}
```

4. We also pass the next one, it is false by default:

```solidity
// @dev Ensure that the migration (minting of NFT) can only be performed once
if (successMigrated == true) {
    revert ErrorsLib.hasMigrated();
}
```

The rest of the function is executed, and successMigrated is set to true even if the users haven’t voted and >50% quorum isn’t reached.

Proof of Concept (PoC)

```solidity
// @notice This function mints the Portal NFT and transfers user stakes
//         to a new Adapter
// @dev Timelock protected function that can only be called once to move
//      capital to a new Adapter
function executeMigration() external isMigrating {
    // @dev Ensure that the timelock has passed
    if (block.timestamp < migrationTime
        && migrationTime > 0) {
        revert ErrorsLib.isTimeLocked();
    }
    // @dev Ensure that the migration (minting of NFT) can only be performed
    //      once
    if (successMigrated == true) {
        revert ErrorsLib.hasMigrated();
    }
    // @dev Mint an NFT to the new Adapter that holds the current Adapter
    //      stake information
    // @dev IMPORTANT: The migration contract must be able to receive ERC721
    //      tokens
    successMigrated = true;
    totalPrincipalStaked = 0;
    PORTAL.mintNFTposition(migrationDestination);
    // @dev Emit migration event
    emit EventsLib.migrationExecuted(migrationDestination);
}
```

```solidity
function testExecuteMigrationWithoutVotes() external {
    help_stake_ETH();
    help_stake_ETH_Bob();
    help_stake_ETH_Karen();
    vm.prank(owner);
    adapter_ETH.proposeMigrationDestination(newAdapterAddr);
    vm.prank(address(1));
    adapter_ETH.executeMigration();
    assertTrue(adapter_ETH.successMigrated());
}
```

## Recommendation
Add additional checks for reached quorum or revert if migrationTime == 0.
