# [C] Random task execution

## Summary
Severity: Critical
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description
In a scenario where user takes a flash loan, `_parseFLAndExecute()` gives the flash loan wrapper contract (`FLAaveV2`, `FLDyDx`) the permission to execute functions on behalf of the user's `DSProxy`. This execution permission is revoked only after the entire recipe execution is finished, which means that in case that any of the external calls along the recipe execution is malicious, it might call `executeAction()` back and inject any task it wishes (e.g. take user's funds out, drain approved tokens, etc)

#### Examples


**code/contracts/actions/flashloan/FLAaveV2.sol:L105-L136**
```solidity
function executeOperation(
    address[] memory _assets,
    uint256[] memory _amounts,
    uint256[] memory _fees,
    address _initiator,
    bytes memory _params
) public returns (bool) {
    require(msg.sender == AAVE_LENDING_POOL, ERR_ONLY_AAVE_CALLER);
    require(_initiator == address(this), ERR_SAME_CALLER);

    (Task memory currTask, address proxy) = abi.decode(_params, (Task, address));

    // Send FL amounts to user proxy
    for (uint256 i = 0; i < _assets.length; ++i) {
        _assets[i].withdrawTokens(proxy, _amounts[i]);
    }

    address payable taskExecutor = payable(registry.getAddr(TASK_EXECUTOR_ID));

    // call Action execution
    IDSProxy(proxy).execute{value: address(this).balance}(
        taskExecutor,
        abi.encodeWithSelector(CALLBACK_SELECTOR, currTask, bytes32(_amounts[0] + _fees[0]))
    );

    // return FL
    for (uint256 i = 0; i < _assets.length; i++) {
        _assets[i].approveToken(address(AAVE_LENDING_POOL), _amounts[i] + _fees[i]);
    }

    return true;
}
```

#### Recommendation
A reentrancy guard (mutex) that covers the entire content of `FLAaveV2.executeOperation`/`FLDyDx.callFunction` should be used to prevent such attack. 
<!--Another solution is to make the Flashloan flow to call `DSProxy` back instead of the `FLAave` contract.-->
