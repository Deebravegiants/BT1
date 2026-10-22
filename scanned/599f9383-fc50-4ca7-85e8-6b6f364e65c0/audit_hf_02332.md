# [M] Potential Reentrancy Risk in MasterChef

## Summary
Severity: Medium
Contest weight: 0.4601
Dataset id: 12678
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A common coding best practice in Solidity is the adherence of checks-effects-interactions principle. This principle is effective in mitigating a serious attack vector known as re-entrancy.
Via this particular attack vector, a malicious contract can be reentering a vulnerable contract in a nested manner. Specifically, it first calls a function in the vulnerable contract, but before the first instance of the function call is finished, second call can be arranged to re-enter the vulnerable contract by invoking functions that should only be executed once. This attack was part of several most prominent hacks in Ethereum history, including the DAO [17] exploit, and the recent Uniswap/Lendf.Me hack [16].
We notice there is an occasion where the checks-effects-interactions principle is violated. Using the MasterChef as an example, the addLiquidityInternal() function (see the code snippet below) is provided to externally call a router contract to add liquidity. However, the invocation of an external contract requires extra care in avoiding the above re-entrancy.
Apparently, the interaction with the external contract (line 463) starts before effecting the update on the internal state (lines 635-636), hence violating the principle. In this particular case, if the external contract has certain hidden logic that may be capable of launching re-entrancy via the deposit() function.
```solidity
function depositByAddLiquidityInternal(address _user, uint256 _pid, uint256 amount0, uint256 amount1) internal {
    // Make sure the currency has been transferred in before that
    PoolInfo memory pool = poolInfo[_pid];
    // Non -VIP pool
    require(address(pool.ticket) == address(0), "T:E");
    uint liquidity = addLiquidityInternal(address(pool.lpToken), _user, amount0, amount1);
    _deposit(_pid, liquidity, _user);
}
function addLiquidityInternal(address lpToken, address _user, uint256 amount0, uint256 amount1) internal returns (uint) {
    // Stack too deep, try removing local variables
    DepositVars memory vars;
    address token0 = IParaPair(lpToken).token0();
    address token1 = IParaPair(lpToken).token1();
    // Go approve
    approveIfNeeded(token0, address(paraRouter), amount0);
    approveIfNeeded(token1, address(paraRouter), amount1);
    // lp balance check
    vars.oldBalance = IParaPair(lpToken).balanceOf(address(this));
    (vars.amountA, vars.amountB, vars.liquidity) = paraRouter.addLiquidity(token0, token1, amount0, amount1, 1, 1, address(this), block.timestamp + 600);
    vars.newBalance = IParaPair(lpToken).balanceOf(address(this));
    require(vars.newBalance > vars.oldBalance, "B:E");
    vars.liquidity = vars.newBalance.sub(vars.oldBalance);
    addChange(_user, token0, amount0.sub(vars.amountA));
    addChange(_user, token1, amount1.sub(vars.amountB));
    return vars.liquidity;
}
function _deposit(uint256 _pid, uint256 _amount, address _user) internal {
    PoolInfo storage pool = poolInfo[_pid];
    UserInfo storage user = userInfo[_pid][_user];
    // add total of pool before updatePool
    poolsTotalDeposit[_pid] = poolsTotalDeposit[_pid].add(_amount);
    updatePool(_pid);
    if (user.amount > 0) {
        uint256 pending = user.amount.mul(pool.accT42PerShare).div(1e12).sub(user.rewardDebt);
        // TODO _claim(pool.pooltype, pending);
    }
    user.amount = user.amount.add(_amount);
    user.rewardDebt = user.amount.mul(pool.accT42PerShare).div(1e12);
    emit Deposit(_user, _pid, _amount);
}
```
Note that other routines share the same issue, including depositTo(), deposit_all_tickets(), withdraw_tickets(), withdraw(), withdraw_tickets(), and depositByAddLiquidityETH() from the same contract as well as supplyFlex(), supplyRegular(), withdrawFlex(), withdrawRegular() from the ParaSupply contract.

## Recommendation
Apply necessary reentrancy prevention by utilizing the nonReentrant modifier to block possible re-entrancy.
