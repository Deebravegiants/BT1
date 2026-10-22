# [M] High risk checks can be bypassed with extra

## Summary
Severity: Medium
Contest weight: 0.6638
Dataset id: 22419
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Adding extra unused bytes to proposal calldata can trick the _isHighRiskProposal() function. The length checks on the transaction calldata of what falls into the 'high risk' proposal category is too strict, and incorrectly fails with extra padding. In solidity, any extra bytes of calldata, beyond what is required to satisfy the function arguments, are ignored, and have no effect on the operation of the function being called.

A proposal that should have been flagged as high risk, is not, and therefore can be passed with the easier, lower, quorum. This violates a critical invariant.

Checks for calls to the kernel's executeAction() function, expect exactly the right number of bytes to satisfy the function arguments, and no more:
// File: src/external/governance/GovernorBravoDelegate.sol : GovernorBravoDelegate._isHighRiskProposal()
#1
// Check if the action is making a core change to system via the kernel
```solidity
if (selector == Kernel.executeAction.selector) {
    uint8 action;
    address actionTarget;
    if (bytes(signature).length == 0 && data.length == 0x44) {
        assembly {
            action := mload(add(data, 0x24)) // accounting for length and selector in first 4 bytes
            actionTarget := mload(add(data, 0x44))
        }
    } else if (data.length == 0x40) {
        (action, actionTarget) = abi.decode(data, (uint8, address));
    } else {
        continue;
    }
}
```
ain/bophades/src/external/governance/GovernorBravoDelegate.sol#L631-L645

this results in an easier quorum threshold:
// File: src/external/governance/GovernorBravoDelegate.sol : GovernorBravoDelegate.propose()
#2
// Identify the quorum level to use
```solidity
if (_isHighRiskProposal(targets, signatures, calldatas)) {
    quorumVotes = getHighRiskQuorumVotes();
} else {
    quorumVotes = getQuorumVotes();
}
```
ain/bophades/src/external/governance/GovernorBravoDelegate.sol#L168-L173

## Proof of Concept
The following test shows that extending the calldata by an empty byte still triggers a valid call to executeAction(), but is categorized as lower severity:
```diff
diff --git a/bophades/src/test/external/GovernorBravoDelegate.t.sol b/bophades/src/test/external/GovernorBravoDelegate.t.sol
index 778163c..bdb6ae2 100644
--- a/bophades/src/test/external/GovernorBravoDelegate.t.sol
+++ b/bophades/src/test/external/GovernorBravoDelegate.t.sol
@@ -386,6 +386,10 @@ contract GovernorBravoDelegateTest is Test {
    assertEq(quorum, 200_000e18);
}
+
function executeAction(Actions action_, address target_) external {
+
    console2.log("executed with extra calldata");
+
}
+
function testCorrectness_proposeCapturesCorrectQuorum_highRisk() public {
    // Activate TRSRY
    vm.prank(address(timelock));
@@ -404,9 +408,12 @@ contract GovernorBravoDelegateTest is Test {
    calldatas[0] = abi.encodeWithSelector(
        kernel.executeAction.selector,
        Actions.ActivatePolicy,
        address(custodian),
+
        ""
    );
+
    address(this).call(calldatas[0]);
+
    vm.prank(alice);
    bytes memory data = address(governorBravoDelegator).functionCall(
        abi.encodeWithSignature(
```
Output:
% forge test --match-test testCorrectness_proposeCapturesCorrectQuorum_highRisk -vv
...
[FAIL. Reason: assertion failed]
testCorrectness_proposeCapturesCorrectQuorum_highRisk() (gas: 568208)
Logs:
executed with extra calldata
Error: a == b not satisfied [uint]
Expected: 300000000000000000000000
Actual: 200000000000000000000000
Test result: FAILED. 0 passed; 1 failed; 0 skipped; finished in 14.92ms
...

## Recommendation
Change length checks to be >=, rather than strict equality, since the function signature already specifies the number of arguments
