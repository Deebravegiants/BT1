# [M] Tap - Controller should not be updateable

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

Similar to the [issue 6.11](/diligence/audits/2019/11/aragonblack-fundraising/#tap-reserve-can-be-updated-in-tap-but-not-in-marketmaker-or-controller), `Tap` allows updating the `Controller` contract it is using. The permission is currently not assigned in the `FundraisingMultisigTemplate` but might be used in custom deployments.


**code/apps/tap/contracts/Tap.sol:L117-L125**
```solidity
/**
 * @notice Update controller to `_controller`
 * @param _controller The address of the new controller contract
*/
function updateController(IAragonFundraisingController _controller) external auth(UPDATE_CONTROLLER_ROLE) {
    require(isContract(_controller), ERROR_CONTRACT_IS_EOA);

    _updateController(_controller);
}
```

#### Recommendation

To avoid inconsistencies, we suggest to remove this functionality and provide a guideline on how to safely upgrade components of the system.
