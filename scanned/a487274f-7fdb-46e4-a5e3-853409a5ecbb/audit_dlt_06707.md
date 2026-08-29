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



_Trimmed to 38 lines — full report: https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/issues/90_
