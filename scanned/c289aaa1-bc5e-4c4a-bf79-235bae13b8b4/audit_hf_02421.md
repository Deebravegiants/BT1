# [M] Accommodation of approve() Idiosyncrasies

## Summary
Severity: Medium
Contest weight: 0.5927
Dataset id: 13022
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Though there is a standardized ERC-20 specification, many token contracts may not strictly follow the specification or have additional functionalities beyond the specification. In this section, we examine the approve() routine and possible idiosyncrasies from current widely-used token contracts. In particular, we use the popular stablecoin, i.e., USDT, as our example. We show the related code snippet below. On its entry of approve(), there is a requirement, i.e., require(!((_value != 0) && (allowed[msg.sender][_spender] != 0))). This specific requirement essentially indicates the need of reducing the allowance to 0 first (by calling approve(_spender, 0)) if it is not, and then calling a second one to set the proper allowance. This requirement is in place to mitigate the known approve()/transferFrom() race condition (https://github.com/ethereum/EIPs/issues/20#issuecomment-263524729).
```solidity
* @dev Approve the passed address to spend the specified amount of tokens on behalf of msg.sender.
* @param _spender The address which will spend the funds.
* @param _value The amount of tokens to be spent.
function approve(address _spender, uint _value) public onlyPayloadSize(2*32) {
    // To change the approve amount you first have to reduce the addresses allowance to zero by calling approve(_spender, 0) if it is not already 0 to mitigate the race condition described here: https://github.com/ethereum/EIPs/issues/20#issuecomment-263524729
    require(!((_value != 0) && (allowed[msg.sender][_spender] != 0)));
    allowed[msg.sender][_spender] = _value;
    Approval(msg.sender, _spender, _value);
}
```
Because of that, a normal call to approve() with a currently non-zero allowance may fail. An example is shown below. It is in the _rebalanceReserve() routine that is designed to rebalance the pool assets. To accommodate the specific idiosyncrasy, there is a need to approve() twice: the first one reduces the allowance to 0; and the second one sets the new allowance.
```solidity
function _rebalanceReserve(uint256 info) internal {
    uint256 pricePerShare;
    uint256 cashUnnormalized;
    uint256 yBalanceUnnormalized;
    (pricePerShare, cashUnnormalized, yBalanceUnnormalized) = _getBalanceDetail(info);
    uint256 tid = _getTID(info);
    // Update _totalBalance with interest
    _updateTotalBalanceWithNewYBlance(tid, yBalanceUnnormalized.mul(_normalizeBalance(info)));
    uint256 targetCash = yBalanceUnnormalized.add(cashUnnormalized).div(10);
    if (cashUnnormalized > targetCash) {
        uint256 depositAmount = cashUnnormalized.sub(targetCash);
        IERC20(address(info)).approve(_yTokenAddresses[tid], depositAmount);
        YERC20(_yTokenAddresses[tid]).deposit(depositAmount);
        _yBalances[tid] = yBalanceUnnormalized.add(depositAmount).mul(_normalizeBalance(info));
    } else {
        YERC20(_yTokenAddresses[tid]).withdraw((targetCash.sub(cashUnnormalized)).mul(W_ONE).div(pricePerShare));
        _yBalances[tid] = yBalanceUnnormalized.sub(targetCash.sub(cashUnnormalized)).mul(_normalizeBalance(info));
    }
}
```
Note that the accommodation of the approve() idiosyncrasy is necessary to ensure a smooth re-balance. Otherwise, the rebalance attempt with inconsistent token contracts may always be reverted.

## Recommendation
Accommodate the above-mentioned idiosyncrasy of approve().
