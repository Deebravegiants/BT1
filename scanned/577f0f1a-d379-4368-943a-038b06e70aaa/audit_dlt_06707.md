# [M] Hardcoded Reward incentive address is incorrect has this address can be subjected to change

## Summary
Severity: Medium
Chain: Smart contract
Component: dTRINITY
Published: 2025-06-17
Source: https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/issues/90
Type: hats-finding

## Details
**Github username:** @Tomiwasa0
  **Twitter username:** --
  **HATS Profile:** [HATS Profile](https://app.hats.finance/profile/Bigsam)

  **Beneficiary:** 0x95f04DaAf8999F9fD232eB61916952Da2CE197A8
  **Submission hash (on-chain):** 0x740f3a7e5356e8b362f39bafb7be7b665ac210e041be16017d6858e65d8c58fd
  **Severity:** medium
  
  **Description:**
  **Description**\

The Dlendcore contract includes a function to get the potential reward earned from the lending pool Reward incentive address, but this was hardcoded but the lending pool (Aave) can change this address through governance decision or due to an ugrade. The incentive address can be set in their contract but Trinity hardcodes this address values making it impossible to claim rewards when this address are updated.

https://github.com/aave/aave-v3-core/blob/782f51917056a53a2c228701058a6c3fb233684a/contracts/protocol/tokenization/base/IncentivizedERC20.sol#L109-L119


```solidity


  /**
   * @notice Returns the address of the Incentives Controller contract
   * @return The address of the Incentives Controller
   */
@audit>>    function getIncentivesController() external view virtual returns (IAaveIncentivesController) {
    return _incentivesController;
  }

  /**
   * @notice Sets a new Incentives Controller
   * @param controller the new Incentives controller
   */
@audit>>    function setIncentivesController(IAaveIncentivesController controller) external onlyPoolAdmin {
    _incentivesController = controller;
  }

```


In dlend core

```solidity
    /* State */

    IPoolAddressesProvider public immutable lendingPoolAddressesProvider;

@audit>>    IRewardsController public immutable dLendRewardsController;
    address public immutable dLendAssetToClaimFor;
    address public immutable targetStaticATokenWrapper;


```

```solidity
    /* RewardClaimable functions */

    /**
     * @dev Claims multiple rewards
     * @param rewardTokens The reward tokens to claim
     * @param receiver The address to receive the claimed rewards
     * @return rewardAmounts The amount of rewards claimed for each token (have the same length as the tokens array)
     */
    function _claimRewards(
        address[] calldata rewardTokens,
        address receiver
    ) internal override returns (uint256[] memory rewardAmounts) {
        if (rewardTokens.length == 0) {
            revert ZeroRewardTokens();
        }
        if (receiver == address(0)) {
            revert ZeroReceiverAddress();
        }

        rewardAmounts = new uint256[](rewardTokens.length);
        address[] memory assetsToClaimForPayload = new address[](1);
        assetsToClaimForPayload[0] = dLendAssetToClaimFor;

        for (uint256 i = 0; i < rewardTokens.length; i++) {
            address rewardToken = rewardTokens[i];
            if (rewardToken == address(0)) {
                revert ZeroAddress(); // Cannot claim zero address token
            }

            uint256 balanceBefore = ERC20(rewardToken).balanceOf(receiver);

            // Claim all available amount of the specific reward token
@audit>>            dLendRewardsController.claimRewardsOnBehalf(
                assetsToClaimForPayload, // Asset held by the wrapper in dLEND
                type(uint256).max, // Claim all
                targetStaticATokenWrapper, // User earning rewards is the wrapper
                receiver,
                rewardToken // The reward token to claim
            );

            uint256 balanceAfter = ERC20(rewardToken).balanceOf(receiver);
            rewardAmounts[i] = balanceAfter - balanceBefore;
        }
        return rewardAmounts;
    }
```

**Attack Scenario**\

1. Hardcoded/ immutable reward incentive address
2. Change/update of this address by lending pool
3. All calls to claim rewards will revert
4. Incentive address cannot be updated since the address is set to immutable with no admin function to update it.
5. All call to claim Reward will Revert from here onwards

**Attachments**

1. **Proof of Concept (PoC) File**
<!-- You must provide a file containing a proof of concept (PoC) that demonstrates the vulnerability you have discovered. -->

2. **Revised Code File (Optional)**

Only the address Provider can be set to immutable, The admin should create an admin function that can update the Reward address.
