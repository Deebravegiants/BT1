# [M] Mitigation Confirmed for M-02

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-05-asymmetry-mitigation
Published: 2023-05-08
Source: https://github.com/code-423n4/2023-05-asymmetry-mitigation-findings/issues/43
Type: code-finding

## Details
# MITIGATION IS NOT CONFIRMED
# MITIGATION IS NOT CONFIRMED

# Mitigation of M-02: Issue not mitigated

Link to Issue: https://github.com/code-423n4/2023-03-asymmetry-findings/issues/1049

## Comment

Issue M-02 describes an edge case in which the SfrxEth derivative may revert under an scenario where the calculation of the redeem amount in the sfrxETH vault is zero, causing a potential DoS in the protocol.

The proposed fix by the sponsor is to use the derivative enable/disable feature, probably with the intention of disabling the SfrxEth in case the issue is manifested. I don't think this fully mitigates the issue for at least two major reasons, which are described below.

## Technical Details

The reasoning for the issue in the original report is that if the derivative weight has been set to 0, then a series of staking/unstaking actions could dilute the amount for the SftxEth derivative and eventually lead to the `withdraw()` being called with 1. 

The proposed mitigation misses a very important detail, which is that the disable feature operates on a global level. While the issue may be experienced by a few users that triggered the particular conditions for this to happen, other users may still have a normal or significant amount of funds in the derivative. The protocol cannot simply disable the derivative just to address the problem of a few, doing so may also lock funds for other users of the protocol.

It should be also noted that the described scenario in the original issue does not represent the only case which may trigger the issue. Any situation where the calculated redeem amount is low enough to be converted to zero assets given the required conditions (total assets and total shares) in the sfrxETH vault will trigger the issue. As a quick example, the following test reproduces the case where the user has a low number of SafEth tokens, note that here the weight of the derivative isn't set to zero:

```solidity
// Test for mitigation contest. MR-M-02
function test_SafEth_SfrxRedeemDos() public {
    address sfrxEthVault = sfrxEth.SFRX_ETH_ADDRESS();
    uint256 totalShares = ISfrxEthVault(sfrxEthVault).totalSupply();

    // Ensure assets is below shares to match conditions in original issue
    vm.store(sfrxEthVault, bytes32(uint256(7)), bytes32(totalShares - 100e18));

    // Setup derivative
    vm.prank(deployer);
    safEth.addDerivative(address(sfrxEth), 1);

    // user has 1 ether
    uint256 initialAmount = 1 ether;
    vm.deal(user, initialAmount);

```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-05-asymmetry-mitigation-findings/issues/43_
