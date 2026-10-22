# [M] Decimals discrepancy causes the incorrect pegging

## Summary
Severity: Medium
Contest weight: 0.6001
Dataset id: 14797
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The StakingToken contract is intended to create a staking token pegged to the underlying token wTAO. According to the NatSpec comments in the IStakingToken interface:
@notice The address of the underlying token that this staking token is pegged to
function underlyingToken() external view returns (address);

However, there's a significant discrepancy due to differing decimal places between the two tokens. The underlying token wTAO has 9 decimals, whereas the staking token has 18 decimals. This difference leads to a misalignment in value representation: Intended Pegging: 1 wTAO (which is 1e9 units considering 9 decimals) should equal 1 staking token (1e18 units with 18 decimals). Actual Behavior: When a user deposits 1 wTAO (1e9 units), they receive 1e9 units of the staking token, which is only 0.000000001 of the staking token when considering its 18 decimals. As a result, the staking token is not correctly pegged to the underlying wTAO token.

```solidity
function test_deposit() public {
    uint256 amount = 1 * 10**mockUnderlyingToken.decimals();
    uint256 minStakingAmount = 1e6;
    uint16 stakingFeeBPS = 0;
    uint256 bridgingFee = 0;
    // Have the config manager set configs
    vm.startPrank(configManager);
    stakingToken.setMinStakingAmount(minStakingAmount);
    stakingToken.setStakingFeeBPS(stakingFeeBPS);
    stakingToken.setBridgingFee(bridgingFee);
    stakingToken.setProtocolVault(protocolVault);
    stakingToken.setMaxDepositPerRequest(type(uint256).max);
    stakingToken.setCap(type(uint256).max);
    vm.stopPrank();
    // Mint the amount of undelying tokens to userA
    mockUnderlyingToken.mint(userA, amount);
    // Have userA approve the staking token to pull the underlying token from
    // them
    vm.prank(userA);
    mockUnderlyingToken.approve(address(stakingToken), amount);
    // Have userA mint the amount of staking tokens
    vm.startPrank(userA);
    stakingToken.deposit(amount);
    vm.stopPrank();
    // Get the staking token balance of userA
    uint256 stakingTokenBalance = stakingToken.balanceOf(userA);
    console.log("balance = %s", stakingTokenBalance);
}
```

POC Output
Ran 1 test for test/Attack.t.sol:AttackTest
[PASS] test_deposit() (gas: 365732)
Logs:
balance = 1000000000
Suite result: ok. 1 passed; 0 failed; 0 skipped; finished in 1.21ms (172.65µs CPU time)
Ran 1 test suite in 3.65ms (1.21ms CPU time): 1 tests passed, 0 failed, 0 skipped (1 total tests)

## Recommendation
To fix the pegging issue, adjust the staking token's decimals or modify the conversion logic to account for the decimal difference: Match Decimals: Set the staking token's decimals to match that of the underlying wTAO token (9 decimals). This ensures a 1:1 pegging between the two tokens.

```solidity
function decimals() public view virtual override returns (uint8) {
    return 9; // Match the underlying wTAO token's decimals
}
```

Adjust Conversion Logic: If changing the staking token's decimals is not feasible, modify the deposit and withdrawal functions to scale the amounts appropriately.
