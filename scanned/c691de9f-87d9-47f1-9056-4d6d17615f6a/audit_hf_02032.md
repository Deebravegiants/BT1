# [H] Potential Reentrancy Risk in flashLoanSimple()

## Summary
Severity: High
Contest weight: 0.6377
Dataset id: 11573
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A common coding best practice in Solidity is the adherence of checks-effects-interactions principle.
This principle is effective in mitigating a serious attack vector known as re-entrancy.
Via this particular attack vector, a malicious contract can be reentering a vulnerable contract in a nested manner. Specifically, it first calls a function in the vulnerable contract, but before the first instance of the function call is finished, second call can be arranged to re-enter the vulnerable contract by invoking functions that should only be executed once. This attack was part of several most prominent hacks in Ethereum history, including the DAO [15] exploit, and the recent Uniswap/Lendf.Me hack [14].
We notice there is an occasion where the checks-effects-interactions principle is violated. Using the FlashLoanLogic as an example, the flashLoanSimple() function (see the code snippet below) is provided to deposit additional tokens into the option contract. However, the invocation of an external contract requires extra care in avoiding the above re-entrancy.
In particular, the interaction with the external contract inside flashLoanSimple() (line 201) starts before effecting the update on the internal state. More importantly, it carries over the stale cache states and apply them for the calculation of protocol-wide interest rates, while ignoring the possibility that it may re-enter to update the protocol state. These updates may be lost since they are overwritten by the stale states!
```solidity
function executeFlashLoanSimple(
    DataTypes.ReserveData storage reserve,
    DataTypes.FlashloanSimpleParams memory params
) external {
    FlashLoanSimpleLocalVars memory vars;
    DataTypes.ReserveCache memory reserveCache = reserve.cache();
    reserve.updateState(reserveCache);
    ValidationLogic.validateFlashloanSimple(reserveCache);
    vars.receiver = IFlashLoanSimpleReceiver(params.receiverAddress);
    vars.totalPremium = params.amount.percentMul(params.flashLoanPremiumTotal);
    vars.amountPlusPremium = params.amount + vars.totalPremium;
    IAToken(reserveCache.aTokenAddress).transferUnderlyingTo(params.receiverAddress, params.amount);
    require(
        vars.receiver.executeOperation(
            params.asset,
            params.amount,
            vars.totalPremium,
            msg.sender,
            params.params
        ),
        Errors.P_INVALID_FLASH_LOAN_EXECUTOR_RETURN
    );
    vars.premiumToProtocol = params.amount.percentMul(params.flashLoanPremiumToProtocol);
    vars.premiumToLP = vars.totalPremium - vars.premiumToProtocol;
    reserve.cumulateToLiquidityIndex(
        IERC20(reserveCache.aTokenAddress).totalSupply(),
        vars.premiumToLP
    );
    reserve.accruedToTreasury =
        reserve.accruedToTreasury +
        Helpers.castUint128(vars.premiumToProtocol.rayDiv(reserve.liquidityIndex));
    reserve.updateInterestRates(reserveCache, params.asset, vars.amountPlusPremium, 0);
    IERC20(params.asset).safeTransferFrom(
        params.receiverAddress,
        reserveCache.aTokenAddress,
        vars.amountPlusPremium
    );
    emit FlashLoan(
        params.receiverAddress,
        msg.sender,
        params.asset,
        params.amount,
        vars.totalPremium,
    );
}
```

## Recommendation
Revise the above flashLoanSimple() routine by applying necessary reentrancy prevention to avoid the use of cached state to overwrite legitimate protocol updates.
