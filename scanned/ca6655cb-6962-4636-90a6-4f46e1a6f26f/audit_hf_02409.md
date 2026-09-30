# [M] Potential Reentrancy in emergencyWithdraw()

## Summary
Severity: Medium
Contest weight: 0.4507
Dataset id: 12960
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A common coding best practice in Solidity is the adherence of checks-effects-interactions principle. This principle is effective in mitigating a serious attack vector known as re-entrancy. Via this particular attack vector, a malicious contract can be reentering a vulnerable contract in a nested manner. Specifically, it first calls a function in the vulnerable contract, but before the first instance of the function call is finished, second call can be arranged to re-enter the vulnerable contract by invoking functions that should only be executed once. This attack was part of several most prominent hacks in Ethereum history, including the DAO [20] exploit, and the recent Uniswap/Lendf.Me hack [19]. We notice there is an occasion where the checks-effects-interactions principle is violated. Using the MasterChef as an example, the emergencyWithdraw() function (see the code snippet below) is provided to externally call a token contract to transfer assets. However, the invocation of an external contract requires extra care in avoiding the above re-entrancy. Apparently, the interaction with the external contract (line 218) starts before affecting the update on internal states (lines 220-221), hence violating the principle. In this particular case, if the external contract has certain hidden logic that may be capable of launching re-entrancy via the same entry function.
```solidity
// Withdraw without caring about rewards. EMERGENCY ONLY.
function emergencyWithdraw(uint256 _pid) public {
    PoolInfo storage pool = poolInfo[_pid];
    UserInfo storage user = userInfo[_pid][msg.sender];
    pool.lpToken.safeTransfer(address(msg.sender), user.amount);
    emit EmergencyWithdraw(msg.sender, _pid, user.amount);
    user.amount = 0;
    user.rewardDebt = 0;
}
```

## Recommendation
Apply necessary reentrancy prevention by utilizing the nonReentrant modifier to block possible re-entrancy. Note other routines deposit() and withdraw() share the same issue.
