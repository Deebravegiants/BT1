# [H] Force Investment Risk in TargetVaultDopple

## Summary
Severity: High
Contest weight: 0.6390
Dataset id: 12067
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Feeder protocol is a decentralized DeFi aggregator for diversified yield generation on Binance Smart Chain (BSC). The investment subsystem is inspired from the yearn.finance framework and thus shares similar architecture with vaults, and strategies. While examining the TargetVaultDopple implementation, we notice a potential force investment risk that has been exploited in earlier hacks, e.g., yDAI [13] and BT.Finance [1]. To elaborate, we show below the related TargetVaultDopple vault. Specifically, new target vault contracts have been designed and implemented to invest VC assets, harvest growing yields, and return any gains, if any, to the investors. In order to have a smooth investment experience, the target vault contract has a dedicated function, i.e., deposit(), that can be invoked to kick off the investment.
```solidity
* @dev Deposit from target vault to target vault
function deposit() external virtual onlyVault {
    _deposit();
    cachedPricePerShare = targetPricePerShare();
}
function _deposit() internal virtual {
    uint256 _balance = token.balanceOf(address(this));
    if (_balance > 0) {
        uint256 _dopBefore = dopLP.balanceOf(address(this));
        // Deposit to Belt to get Dopple token.
        token.safeIncreaseAllowance(address(dopPool), _balance);
        uint256[] memory amounts = new uint256[](dopPoolLength);
        amounts[getDoppleTokenIndex()] = _balance;
        dopPool.addLiquidity(amounts, 0, block.timestamp + 600);
        uint256 _dopAfter = dopLP.balanceOf(address(this));
        _balance = _dopAfter.sub(_dopBefore);
        depositedBalance = _balance;
        dopLP.safeIncreaseAllowance(address(doppleStaking), _balance);
        doppleStaking.deposit(address(this), pid, _balance);
        emit Deposited(_balance);
    }
}
```
It comes to our attention that the deposit() function is not guarded or can be invoked by any one to initiate the investment. If the configured strategy blindly invests the deposited funds into an imbalanced Dopple pool, the strategy will not result in a profitable investment. In fact, earlier incidents (yDAI and BT hacks [13, 1]) have prompted the need of a guarded call to the investment function. For the very same reason, we argue for the guarded call to block potential flashloan-assisted attacks. One mitigation will enforce certain lockup period for investment.

## Recommendation
Develop the lockup time period to block unwanted flashloan attacks. And take extra care in ensuring the vault assets will not be blindly deposited into a faulty target vault (that is currently not making any profit).
