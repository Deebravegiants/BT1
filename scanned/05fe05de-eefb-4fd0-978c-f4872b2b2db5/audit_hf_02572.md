# [M] `setUpdateWeightRunnerAddress` could break the protocol

## Summary
Severity: Medium
Contest weight: 0.8278
Dataset id: 13892
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The current implementation of UpdateWeightRunner introduces a critical vulnerability in the protocol. If the quantammAdmin modifies the UpdateWeightRunner, it could lead to unexpected behavior where the protocol breaks. Specifically:
A new UpdateWeightRunner might have a different quantammAdmin, which would not align with the existing Pool.
The rule required by the new UpdateWeightRunner is not set because the rule is defined during the Pool initialization phase.

This issue creates inconsistencies in the protocol, potentially leading to a denial of service (DoS) for affected pools.

The vulnerability arises when the UpdateWeightRunner is changed, causing critical issues:
Admin Ownership Mismatch: The new UpdateWeightRunner may have a different quantAdmin, leading to conflicting authority and governance inconsistencies.
Missing Rules: The pool’s rules, set during initialization, are not carried over to the new UpdateWeightRunner. This prevents updates, effectively causing a denial-of-service (DoS) for the pool.

Proof of Concept (POC)
Add the following test to QuantAMMWeightedPool2TokenTest to simulate the issue:

Initialization of the New UpdateWeightRunner:
```solidity
updateWeightRunner1 = new MockUpdateWeightRunner(owner, addr2, false); // Add this to the constructor
```

POC Test Case:
```solidity
MockUpdateWeightRunner updateWeightRunner1;

function testQuantAMMWeightedPoolGetNormalizedWeightsInitial_andThenChangeUpdateWeightRunner() public {
    QuantAMMWeightedPoolFactory.NewPoolParams memory params = _createPoolParams();
    params._initialWeights[0] = 0.6e18;
    params._initialWeights[1] = 0.4e18;

    (address quantAMMWeightedPool, ) = quantAMMWeightedPoolFactory.create(params);

    uint256[] memory weights = QuantAMMWeightedPool(quantAMMWeightedPool).getNormalizedWeights();

    int256[] memory newWeights = new int256[](4);
    newWeights[0] = 0.6e18;
    newWeights[1] = 0.4e18;
    newWeights[2] = 0e18;
    newWeights[3] = 0e18;

    uint64[] memory lambdas = new uint64[](1);
    lambdas[0] = 0.2e18;

    int256[] memory parameters = new int256[](1);
    parameters[0] = 0.2e18;

    address[][] memory oracles = new address[][](1);
    oracles[0] = new address[](1);
    oracles[0][0] = address(chainlinkOracle);

    MockMomentumRule momentumRule = new MockMomentumRule(owner);

    // Change UpdateWeightRunner
    vm.prank(owner);
    QuantAMMWeightedPool(quantAMMWeightedPool).setUpdateWeightRunnerAddress(address(updateWeightRunner1));
    
    QuantAMMWeightedPool(quantAMMWeightedPool).initialize(
        newWeights,
        IQuantAMMWeightedPool.PoolSettings(
            new IERC20[](0),
            IUpdateRule(momentumRule),
            oracles,
            60,
            lambdas,
            0.2e18,
            0.2e18,
            0.2e18,
            parameters,
            address(0)
        ),
        newWeights,
        newWeights,
        10
    );

    // Perform an update with the new runner
    vm.prank(owner);
    updateWeightRunner1.setApprovedActionsForPool(quantAMMWeightedPool, 1);
    updateWeightRunner1.performUpdate(quantAMMWeightedPool);
}
```

Changing the UpdateWeightRunner leads to the following issues:
Denial of Service (DoS):
   The new UpdateWeightRunner does not inherit the rule for the existing pool, rendering it non-functional.
Unauthorized Updates:
   The quantAdmin of the initial UpdateWeightRunner can update the pool with the new UpdateWeightRunner, creating further inconsistencies.

These flaws disrupt the protocol and can lead to operational outages or malicious misuse.

## Proof of Concept
Add the following test to QuantAMMWeightedPool2TokenTest to simulate the issue:

Initialization of the New UpdateWeightRunner:
```solidity
updateWeightRunner1 = new MockUpdateWeightRunner(owner, addr2, false); // Add this to the constructor
```

POC Test Case:
```solidity
MockUpdateWeightRunner updateWeightRunner1;

function testQuantAMMWeightedPoolGetNormalizedWeightsInitial_andThenChangeUpdateWeightRunner() public {
    QuantAMMWeightedPoolFactory.NewPoolParams memory params = _createPoolParams();
    params._initialWeights[0] = 0.6e18;
    params._initialWeights[1] = 0.4e18;

    (address quantAMMWeightedPool, ) = quantAMMWeightedPoolFactory.create(params);

    uint256[] memory weights = QuantAMMWeightedPool(quantAMMWeightedPool).getNormalizedWeights();

    int256[] memory newWeights = new int256[](4);
    newWeights[0] = 0.6e18;
    newWeights[1] = 0.4e18;
    newWeights[2] = 0e18;
    newWeights[3] = 0e18;

    uint64[] memory lambdas = new uint64[](1);
    lambdas[0] = 0.2e18;

    int256[] memory parameters = new int256[](1);
    parameters[0] = 0.2e18;

    address[][] memory oracles = new address[][](1);
    oracles[0] = new address[](1);
    oracles[0][0] = address(chainlinkOracle);

    MockMomentumRule momentumRule = new MockMomentumRule(owner);

    // Change UpdateWeightRunner
    vm.prank(owner);
    QuantAMMWeightedPool(quantAMMWeightedPool).setUpdateWeightRunnerAddress(address(updateWeightRunner1));
    
    QuantAMMWeightedPool(quantAMMWeightedPool).initialize(
        newWeights,
        IQuantAMMWeightedPool.PoolSettings(
            new IERC20[](0),
            IUpdateRule(momentumRule),
            oracles,
            60,
            lambdas,
            0.2e18,
            0.2e18,
            0.2e18,
            parameters,
            address(0)
        ),
        newWeights,
        newWeights,
        10
    );

    // Perform an update with the new runner
    vm.prank(owner);
    updateWeightRunner1.setApprovedActionsForPool(quantAMMWeightedPool, 1);
    updateWeightRunner1.performUpdate(quantAMMWeightedPool);
}
```

## Recommendation
To address this vulnerability, update the setUpdateWeightRunnerAddress function to synchronize quantammAdmin and ensure the rule is correctly set during the update. Modify the function as follows:

```diff
function setUpdateWeightRunnerAddress(address _updateWeightRunner) external override {
    require(msg.sender == quantammAdmin, "ONLYADMIN");
    updateWeightRunner = UpdateWeightRunner(_updateWeightRunner);
    quantammAdmin = updateWeightRunner.quantammAdmin();
    _setRule(); // Call set rule with the correct parameters
    emit UpdateWeightRunnerAddressUpdated(address(updateWeightRunner), _updateWeightRunner);
}
```
