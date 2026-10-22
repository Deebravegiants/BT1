# [M] emergency_shutdownrole is not enough for emer-

## Summary
Severity: Medium
Contest weight: 0.5807
Dataset id: 20491
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Let's examine the function emergencyShutdown():
```solidity
function emergencyShutdown() external onlyRole("emergency_shutdown") {
    active = false;
    // If necessary, defund sDAI.
    uint256 sdaiBalance = sdai.balanceOf(address(this));
    if (sdaiBalance != 0) defund(sdai, sdaiBalance);
    // If necessary, defund DAI.
    uint256 daiBalance = dai.balanceOf(address(this));
    if (daiBalance != 0) defund(dai, daiBalance);
    emit Deactivated();
}
```
This has the modifier onlyRole("emergency_shutdown"). However, this also calls function defund(), which has the modifier onlyRole("cooler_overseer") ```solidity function defund(ERC20 token_, uint256 amount_) public onlyRole("cooler_overseer") { ``` Therefore, the role emergency_shutdown will not have the ability to shutdown the protocol, unless it also has the overseer role. emergency_shutdown role cannot emergency shutdown the protocol

## Proof of Concept
To get a coded PoC, make the following modifications to the test case: lob/main/Cooler/src/test/Clearinghouse.t.sol#L125 //rolesAdmin.grantRole("cooler_overseer", overseer); rolesAdmin.grantRole("emergency_shutdown", overseer); • Run the following test command (to just run a single test test_emergencyShutdown()): forge test --match-test test_emergencyShutdown The test will fail with the ROLES_RequireRole() error.

## Recommendation
There are two ways to mitigate this issue: • Separate the logic for emergency shutdown and defunding. i.e. do not defund when emergency shutdown, but rather defund separately after shutdown. • Move the defunding logic to a separate internal function, so that emergency shutdown function can directly call defunding without going through a modifier.
