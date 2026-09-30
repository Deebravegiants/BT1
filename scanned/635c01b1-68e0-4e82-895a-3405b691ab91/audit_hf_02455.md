# [M] Revisited undelegate() Logic

## Summary
Severity: Medium
Contest weight: 0.4252
Dataset id: 13160
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function undelegate() external payable override whenNotPaused onlyRole(BOT) returns (uint256 _uuid, uint256 _amount) {
    uint256 relayFee = IStaking(nativeStaking).getRelayerFee();
    uint256 relayFeeReceived = msg.value;
    require(relayFeeReceived >= relayFee, "Insufficient RelayFee");
    _uuid = nextUndelegateUUID++; // post-increment: assigns the current value first and then increments
    uint256 totalSnBnbToBurn_ = totalSnBnbToBurn; // To avoid Reentrancy attack
    _amount = convertSnBnbToBnb(totalSnBnbToBurn_);
    _amount -= _amount % TEN_DECIMALS;
    require(reserveAmount >= IStaking(nativeStaking).getDelegated(address(this), bcValidator), "Insufficient Delegate Amount");
    require(_amount + reserveAmount >= IStaking(nativeStaking).getMinDelegation(), "Insufficient Withdraw Amount");
    Public
    uuidToBotUndelegateRequestMap[_uuid] = BotUndelegateRequest({
        startTime: 0,
        endTime: 0,
        amount: _amount,
        amountInSnBnb: totalSnBnbToBurn_
    });
    totalDelegated -= _amount;
    totalSnBnbToBurn = 0;
    ISnBnb(snBnb).burn(address(this), totalSnBnbToBurn_);
    undelegate through native staking contract
    IStaking(nativeStaking).undelegate{value: msg.value}(bcValidator, _amount + reserveAmount);
    emit UndelegateReserve(reserveAmount);
}
```

## Recommendation
Revise the above-mentioned routine to properly handle the undelegate logic.
