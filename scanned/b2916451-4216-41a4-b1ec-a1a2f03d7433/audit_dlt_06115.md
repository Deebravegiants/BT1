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
        IERC20(UNDERLYING_ASSET_ADDRESS).transfer(msg.sender, balance);
    }

}
```

The verified tranche admin will attack as follows:
1. Deploy the `FakeAToken` contract above with following constructor arguments:
    - underlying token address that is currently staked and to be stolen
    - actual tranche Id of which the attacker is verified admin
    - amount of underlying currently staked
2. Call [`ExternalRewardDistributor.beginStakingReward()`](https://github.com/hats-finance/VMEX-0xb6861bdeb368a1bf628fc36a36cec62d04fb6a77/blob/f7659c4513298350b3d477a70588adb3186ab28b/packages/contracts/contracts/protocol/incentives/ExternalRewardDistributor.sol#L175) with following arguments:
      - fake aToken address
      - actual staking contract where the underlying to be stolen is staked
  
    2.1 `onlyVerifiedTrancheAdmin(IAToken(aToken)._tranche())` modifier will pass since `msg.sender` is the actual verified admin of the fake aToken's `_tranche`.

    2.2 `stakingData[aToken] = stakingContract` at L186 will map the fake aToken address to the actual staking contract for the underlying.

    2.3 `uint256 amount = IERC20(aToken).totalSupply()` at L192 will be `0` so the `if` block is skipped.

3. Call [`ExternalRewardDistributor.removeStakingReward()`](https://github.com/hats-finance/VMEX-0xb6861bdeb368a1bf628fc36a36cec62d04fb6a77/blob/f7659c4513298350b3d477a70588adb3186ab28b/packages/contracts/contracts/protocol/incentives/ExternalRewardDistributor.sol#L87) with the fake aToken address as argument.

    3.1 at L90, `uint256 amount = IERC20(aToken).totalSupply()` will be the amount of underlying staked into the staking contract.

    3.2 Inside [`unstake(aToken, amount)`](https://github.com/hats-finance/VMEX-0xb6861bdeb368a1bf628fc36a36cec62d04fb6a77/blob/f7659c4513298350b3d477a70588adb3186ab28b/packages/contracts/contracts/protocol/incentives/ExternalRewardDistributor.sol#L227C16-L227C16), `stakingData[aToken]` has been previously set to the correct `stakingContract` for the underlying, so the underlying will be unstaked correctly.

    3.3 `IERC20(underlying).safeTransfer(aToken, amount)` at L93 transfers the unstaked underlying to the fake aToken contract.

4. Call `FakeAToken.send()` to get the stolen underlying.

Note that this allows the attacker to steal the full amount of staked underlying token and not only the amount staked coming from its own tranche.
To steal all different staked underlying tokens, this can be repeated many times with different fake aTokens each with a different underlying and corresponding staking contract.

## Recommendation
In functions `removeStakingReward()` and `beginStakingReward()` check that the `aToken` passed is indeed a valid aToken, adding the following require statement:

```solidity
require(ILendingPool(addressesProvider.getLendingPool()).getReserveData(underlying, IAToken(aToken)._tranche()).aTokenAddress == aToken, "Incorrect aToken");
```
