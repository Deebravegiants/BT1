# [M] Incorrect calculations in `debtCeiling`

## Summary
Severity: Medium
Contest weight: 0.7221
Dataset id: 19615
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is an incorrect calculation of the debt ceiling for a gauge when its weight is changed. The function that returns the ceiling only adjusts the gauge's own weight by the supplied delta, but it leaves the total weight of all gauges of the same type unchanged. Because the ceiling is derived from the ratio of the gauge weight to the total type weight, failing to update the total weight breaks the invariant that the sum of all gauge weights equals the total type weight. When a user tries to decrement the gauge weight while there is an outstanding loan (issuance), the contract checks whether the remaining issuance fits within the new ceiling. Due to the stale total weight, the computed ceiling is lower than it should be, causing the require statement to revert with the message "GuildToken: debt ceiling used". From the user’s perspective the transaction fails and the user cannot withdraw Guild tokens from the gauge, even though the gauge is the only one of its type and should have an unlimited ceiling. The impact is that token holders are blocked from withdrawing their assets, effectively locking funds. The issue appears only in the edge case where a gauge weight delta is applied and there is at least one loan; in normal operation with multiple gauges the error may be less visible. It was discovered during a Code4rena audit when a test case demonstrated that a single‑gauge scenario reverted unexpectedly. The bug is hard to notice because the function appears to read the correct gauge weight and the logic for unlimited ceilings is present, but the missing adjustment to totalWeight silently violates the accounting assumption that gaugeWeight == totalWeight for a single gauge. The vulnerability belongs to the class of arithmetic or invariant‑violation bugs in financial accounting logic. To fix the issue the function must apply the same delta to the total type weight, or restructure the ceiling calculation to treat the single‑gauge case as unlimited after the weight change, thereby restoring the correct relationship between gauge weight and total weight and preventing erroneous reverts.

## Proof of Concept
If there is a loan in the gauge and user wants to decrement the weight, we need to check it’s ceiling first:

```solidity
// check if gauge is currently using its allocated debt ceiling.
// To decrement gauge weight, guild holders might have to call loans if the debt ceiling is used.
uint256 issuance = LendingTerm(gauge).issuance();
if (issuance != 0) {
    uint256 debtCeilingAfterDecrement = LendingTerm(gauge).debtCeiling(-int256(weight));
    require(
        issuance <= debtCeilingAfterDecrement,
        "GuildToken: debt ceiling used"
    );
}
```

This is needed to ensure that loans are distributed between the gauges according to their weights and tolerance. This only matters if there are multiple gauges of the same type. If there is, only one gauge ceiling is limited by the hardcap and the minter buffer.

```solidity
} else if (gaugeWeight == totalWeight) {
    // one gauge, unlimited debt ceiling
    // returns min(hardCap, creditMinterBuffer)
    return
        _hardCap < creditMinterBuffer ? _hardCap : creditMinterBuffer;
}
```

Unfortunately, `debtCeiling(int256 gaugeWeightDelta)` applies delta only to the `gaugeWeight` leaving `totalWeight` as-is:

```solidity
function debtCeiling(
    int256 gaugeWeightDelta
) public view returns (uint256) {
    address _guildToken = refs.guildToken; // cached SLOAD
    uint256 gaugeWeight = GuildToken(_guildToken).getGaugeWeight(
        address(this)
    );
    gaugeWeight = uint256(int256(gaugeWeight) + gaugeWeightDelta);
    uint256 gaugeType = GuildToken(_guildToken).gaugeType(address(this));
    uint256 totalWeight = GuildToken(_guildToken).totalTypeWeight(
        gaugeType
    );
```

Check this test case for `GuildToken.t.sol`, where the user is unable to withdraw tokens from the gauge even it it’s the only gauge of it’s type and ceiling should be “unlimited”.

Modify `debtCeiling` to act like a `LendingTerm`:

```solidity
function debtCeiling(int256 gaugeWeightDelta) public view returns (uint256) {
    uint256 gaugeWeight = token.getGaugeWeight(address(this));
    gaugeWeight = uint256(int256(gaugeWeight) + gaugeWeightDelta);
    uint256 gaugeType = token.gaugeType(address(this));
    uint256 totalWeight = token.totalTypeWeight(gaugeType);
    if (gaugeWeight == 0) {
        return 0; // no gauge vote, 0 debt ceiling
    } else if (gaugeWeight == totalWeight) {
        // one gauge, unlimited debt ceiling
        // return unlimited
        return 1_000_000 ether;
    }
    uint256 _issuance = issuance; // cached SLOAD
    uint256 totalBorrowedCredit = credit.totalSupply();
    uint256 gaugeWeightTolerance = 1e18;
    if (totalBorrowedCredit == 0 && gaugeWeight != 0) {
        // first-ever CREDIT mint on a non-zero gauge weight term
        // does not check the relative debt ceilings
        return 1_000_000 ether;
    }
    uint256 toleratedGaugeWeight = (gaugeWeight * gaugeWeightTolerance) /
        1e18;
    uint256 debtCeilingBefore = (totalBorrowedCredit *
        toleratedGaugeWeight) / totalWeight;
    if (_issuance >= debtCeilingBefore) {
        return debtCeilingBefore; // no more borrows allowed
    }
    uint256 remainingDebtCeiling = debtCeilingBefore - _issuance; // always >0
    if (toleratedGaugeWeight >= totalWeight) {
        // if the gauge weight is above 100% when we include tolerance,
        // the gauge relative debt ceilings are not constraining.
        return 1_000_000 ether;
    }
    uint256 otherGaugesWeight = totalWeight - toleratedGaugeWeight; // always >0
    uint256 maxBorrow = (remainingDebtCeiling * totalWeight) /
        otherGaugesWeight;
    uint256 _debtCeiling = _issuance + maxBorrow;
    // return min(creditMinterBuffer, hardCap, debtCeiling)
    if (1_000_000 ether < _debtCeiling) {
        return 1_000_000 ether;
    }
    return _debtCeiling;
}
```

run the test

```solidity
function testDebtCeilingOneGauge() public {
    // grant roles to test contract
    vm.startPrank(governor);
    core.grantRole(CoreRoles.CREDIT_MINTER, address(this));
    core.grantRole(CoreRoles.GUILD_MINTER, address(this));
    core.grantRole(CoreRoles.GAUGE_ADD, address(this));
    core.grantRole(CoreRoles.GAUGE_REMOVE, address(this));
    core.grantRole(CoreRoles.GAUGE_PARAMETERS, address(this));
    vm.stopPrank();

    // setup
    token.mint(alice, 100e18);

    token.setMaxGauges(3);
    token.addGauge(1, address(this));

    vm.startPrank(alice);
    token.incrementGauge(address(this), 10e18);
    vm.stopPrank();

    credit.mint(alice, 100e18);
    issuance = 100e18;

    vm.prank(alice);
    // will revert with "GuildToken: debt ceiling used"
    token.decrementGauge(address(this), 8e18);
}
```

## Recommendation
Apply delta to `totalWeight` as well:

```solidity
function debtCeiling(
    int256 gaugeWeightDelta
) public view returns (uint256) {
    address _guildToken = refs.guildToken; // cached SLOAD
    uint256 gaugeWeight = GuildToken(_guildToken).getGaugeWeight(
        address(this)
    );
    gaugeWeight = uint256(int256(gaugeWeight) + gaugeWeightDelta);
    uint256 gaugeType = GuildToken(_guildToken).gaugeType(address(this));
    uint256 totalWeight = GuildToken(_guildToken).totalTypeWeight(
        gaugeType
    );
    totalWeight = uint256(int256(totalWeight) + gaugeWeightDelta);
```
