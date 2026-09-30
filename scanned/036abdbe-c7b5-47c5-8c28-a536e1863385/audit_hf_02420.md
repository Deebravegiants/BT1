# [M] Revisited Trust on Admin Keys

## Summary
Severity: Medium
Contest weight: 0.4627
Dataset id: 13020
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In SmoothyV1, there is a privileged contract, i.e., owner, that plays a critical role in configuring and regulating the system-wide operations (e.g., soft/hard weight adjustment and yToken assignment). Note the yToken assignment directly affects the investment of deposited assets in the pool. In the following, we show the contract's setYEnabled() implementation. This routine may retrieve back the full investment on previous yToken (line 314). The returned assets will be deposited into the new yToken during the rebalance operation occurred in next swap()/mint()/redeem()/rebalance() call.
```solidity
function setYEnabled(uint256 tid, address yAddr) external onlyOwner {
    uint256 info = _tokenInfos[tid];
    if (_yTokenAddresses[tid] != address(0x0)) {
        Withdraw all tokens from yToken, and clear yBalance.
        uint256 cash = _getCashBalance(info);
        YERC20(_yTokenAddresses[tid]).withdraw(YERC20(_yTokenAddresses[tid]).balanceOf(address(this)));
        uint256 dcash = _getCashBalance(info).sub(cash);
        // Update _totalBalance with interest
        _updateTotalBalanceWithNewYBlance(tid, dcash);
        _yBalances[tid] = 0;
    }
    info = _setYEnabled(info, yAddr != address(0x0));
    _yTokenAddresses[tid] = yAddr;
    _tokenInfos[tid] = info;
    // If yAddr != 0x0, we will rebalance in next swap/mint/redeem/rebalance call.
}
```
We emphasize that the current privilege assignment to owner is appropriate and necessary1. However, it is worrisome if owner is not governed by a DAO-like structure. The discussion with the team has confirmed that the governance will be managed by a multisig account. To further eliminate the administration key concern, it may be required to transfer the role to a community-governed DAO. In the meantime, a timelock-based mechanism might also be applicable for mitigation. We point out that a compromised owner account would allow the attacker to add a malicious yToken to steal all funds in the pool, which directly undermines the integrity of the entire protocol.

## Recommendation
Promptly transfer the owner privilege to the intended DAO-like governance contract. And activate the normal on-chain community-based governance life-cycle and ensure the intended trustless nature and high-quality distributed governance.
