# [M] Potential Reentrancy Risk in sendCollateral()

## Summary
Severity: Medium
Contest weight: 0.5931
Dataset id: 12011
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A common coding best practice in Solidity is the adherence of checks-effects-interactions principle. This principle is effective in mitigating a serious attack vector known as re-entrancy. Via this particular attack vector, a malicious contract can be reentering a vulnerable contract in a nested manner. Specically, it first calls a function in the vulnerable contract, but before the first instance of the function call is finished, second call can be arranged to re-enter the vulnerable contract by invoking functions that should only be executed once. This attack was part of several most prominent hacks in Ethereum history, including the DAO [11] exploit, and the recent Uniswap/Lendf.Me hack [10]. We notice there is an occasion where the checks-effects-interactions principle is violated. In the ActivePool contract, the sendCollateral() function (see the code snippet below) is provided to transfer the given amounts of collaterals to the given account by externally calling the collaterals contracts. However, the invocation of an external contract requires extra care in avoiding the above re-entrancy. Apparently, the interaction with the external contract (line 163) may start before the transferring of other collaterals that will update the token balances of the contract, hence violating the principle.
```solidity
function sendCollateral(
    address _account,
    address[] memory _collaterals,
    uint256[] memory _amounts
) external override {
    _requireCallerIsBOorTroveMorSP();
    uint256 collLen = _collaterals.length;
    address collateral;
    uint256 amount;
    bool flag = _notNeedsToSwitchWETH(_account);
    for (uint256 i = 0; i < collLen; ) {
        collateral = _collaterals[i];
        amount = _amounts[i];
        if (amount != 0) {
            if (collateral != address(WETH)) {
                _sendCollateral(_account, collateral, amount);
            } else {
                if (flag) {
                    _sendCollateral(_account, collateral, amount);
                } else {
                    _sendETH(_account, amount);
                }
            }
        }
        unchecked {
            i++;
        }
    }
}
```
Specifically, in the case when the recipient of _sendETH() is a contract, it could hijack a call to the protocol before the transferring of other collaterals. Within the receive()/fallback() functions of the recipient contract, it could call the functions in the protocol that will fetch the collaterals balances of the ActivePool contract, e.g, the ActivePool::getTotalCollateral() routine as the code shown below. Since the other collaterals except for ETH are not transferred out yet, the IERC20Upgradeable(collaterals[i]).balanceOf(address(this)) (line 114) will return a larger value. Generally the collaterals balances are used to calculate the total collateral ratio TCR, which is further used to check if the protocol is in recovery mode or normal mode. Similarly, if some collateral has a callback function, e.g., ERC777, it can also hijack a call to the protocol from the callback function. Based on this, we suggest to properly protect the key functions with the nonReentrant modifier. Another option is to always transfer ETH at last if ETH is the only collateral that has callback function.
```solidity
function getTotalCollateral()
    public
    view
    override
    returns (
        uint256 total,
        address[] memory collaterals,
        uint256[] memory amounts
    )
{
    collaterals = ITroveManager(troveManagerAddress).getCollateralSupport();
    uint256 collLen = collaterals.length;
    amounts = new uint256[](collLen);
    for (uint256 i = 0; i < collLen; ) {
        amounts[i] = IERC20Upgradeable(collaterals[i]).balanceOf(address(this));
        total = total.add(amounts[i]);
        unchecked {
            i++;
        }
    }
}
```
Note the same issue is also applicable to the StabilityPool::_sendCollateralGainToDepositor()/CollSurplusPool::claimColl() routines, etc.

## Recommendation
Apply the checks-effects-interactions design pattern or add the nonReentrant guard modifier.
