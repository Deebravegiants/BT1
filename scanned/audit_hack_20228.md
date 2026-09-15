# [M] 5.3.7 AeraVault constructoris not checking all the input parameters

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk
**Context:** AeraVaultV1.sol#L260-L
**Description:** TheAera Vaultconstructor has the role to handle Balancer’sManagedPooldeployment. The con-
structor should increase the number of user input validation and theGauntletteam should be aware of the possible
edge case that could happen given that the deployment of theAera Vaultis handled directly by the Treasury and
not by the Gauntlet team itself.
We are going to list all the worst-case scenarios that could happen given the premise that the deployments are
handled by the Treasury.

1. factorycould be a wrapper contract that will deploy aManagedPool. This would mean that the deployer could
    pass correct parameters toAera Vaultto pass these checks, but will use custom and malicious parameters
    on thefactorywrapper to deploy the real Balancer pool.
2. swapFeePercentagevalue is not checked. On Balancer, the deployment will revert if the value is not in-
    side this range>= 1e12 (0.0001%) and <= 1e17 (10% - this fits in 64 bits). Without any check,
    the Gauntlet accept to follow the Balancer’s swap requirements.
3. manager_is not checked. They could set the manager as the Treasury (owner of the vault) itself. This would
    give the Treasury the full power to manage the Vault. At least these values should be checked:address(0),
    address(this)orowner(). The same checks should also be done in thesetManager()function.
4. validator_could be set to a custom contract that will give full allowances to the Treasury. This would make
    thewithdraw()act likefinalize()allowing to withdraw all the funds from the vault/pool.


5. noticePeriod_has only a max value check. Gauntlet team explained that a time delay between the ini-
    tialization of the finalize process and the actualfinalizeis needed to prevent the Treasury to be able to
    instantly withdraw all the funds. Not having a min value check allow the Treasury to set the value to 0 so
    there would be no delay between theinitiateFinalization()andfinalize()becausenoticeTimeoutAt
    == block.timestamp.
6. managementFee_has no minimum value check. This would allow the Treasury to not pay the manager
    because themanagerFeeIndexwould always be 0.
7. description_can be empty. From the Specification PDF, the description of the vault has the role to “De-
    scribes vault purpose and modelling assumptions for differentiating between vaults”. Being empty could lead
    to a bad UX for external services that needs to differentiate different vaults.
These are all the checks that are done directly by Balancer during deployment via the Pool Factory:
- BasePool constructor#L94-L95min and max number of tokens.
- BasePool constructor#L102token array is sorted following Balancer specification (sorted by token address).
- BasePool constructor calling _setSwapFeePercentagemin and max value forswapFeePercentage.
- BasePool constructor calling vault.registerTokens token address uniqueness (can’t have same
token in the pool), it also checks thattoken != IERC20(0). Following the pathBasePool is calling
vault.registerTokens that should call function _registerMinimalSwapInfoPoolTokens from
MinimalSwapInfoPoolsBalance.
- ManagedPool constructor calling _startGradualWeightChange Check min value of weight and that the total
sum of the weights are equal to 100%. _startGradualWeightChangeinternally check thatendWeight >=
WeightedMath._MIN_WEIGHTandnormalizedSum == FixedPoint.ONE.
**Recommendation:**
- Create a factory to wrap bothAeraVaultandValidatordeployment to reduce influence and possible mali-
cious attack from external actors.
- Add a custom min/max value check forswapFeePercentageon top of Balancer’s check if needed.
- Add checks on manager_ value to prevent an empty manager (address(0)) or that the manager
andAeraVaultowner will be equal to the Treasury itself.
- Added a min value check to thenoticePeriod_parameter if needed to prevent that the time betweenini-
tiateFinalizationandfinalizecall is too small.
- Add a min value check to themanagementFee_parameter if needed to prevent the Treasury to not pay the
manager.
- Add a check ondescription_to prevent to deploy aAeraVaultwith an empty description that would create
confusion on web application that will display similar vaults.
- Check meticulously that future Balancer’s version still maintain the same checks listed above. Consider
replicating those checks during deployment to be future-proof.
We also recommend carefully documenting the possible consequences of supporting "special" types of tokens:
- Token with more than 18 decimals that are **not supported** by Balancer.
- Token with small number of decimals.
- ERC777 tokens.
- Token with fees on transfer.
- Token with blacklisting capabilities.
**Gauntlet:** In our trust model, we only decide to manage the vault if it has been correctly deployed. So leaving the
focus to be on human error, I think the following are actionable:
3. (manager checks)


```
Add checks on manager_ value to prevent an empty manager (address(0)) or that the manager
andAera Vaultowner will be equal to the Treasury itself
```
4. (description checks)
    Add a check on description_ to prevent to deploy aAera Vaultwith an empty description that
    would create confusion on web application that will display similar vaults.
I’ll also take a documentation action for these:
Token with more than 18 decimals that are not supported by Balancer Token with small number of
decimals ERC777 tokens Token with fees on transfer Token with blacklisting capabilities
