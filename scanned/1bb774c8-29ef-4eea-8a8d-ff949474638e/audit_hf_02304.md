# [M] Vesting Bypass With transferFrom()

## Summary
Severity: Medium
Contest weight: 0.4253
Dataset id: 12563
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As mentioned in Section 3.1, the Nested protocol has its own governance token NST with the unique support of dynamic vesting schedules. Our analysis shows that the vesting may be bypassed.
To elaborate, we show below the transfer()/approve() routines. Suppose there is a new grant of 100 NSTs with the intended beneﬁciary Alice and the grant is restricted according to the speciﬁc vesting schedule. However, Alice can call approve() to allow Malice to spend on his behalf. With that Malice can immediately spend the granted 100 NSTs without being subject to the vesting schedule.
```solidity
/**
 * @dev Methods transfer() and approve() require additional available funds check
 * to prevent spending held but non-vested tokens. Note that transferFrom() does NOT
 * have this additional check because approved funds come from an already set-aside
 * allowance, not from the wallet.
 */
function transfer(address to, uint256 value) public override onlyIfFundsAvailableNow(msg.sender, value) returns (bool) {
    return super.transfer(to, value);
}

/**
 * @dev Additional available funds check to prevent spending held but non-vested tokens.
 */
function approve(address spender, uint256 value) public override onlyIfFundsAvailableNow(msg.sender, value) returns (bool) {
    return super.approve(spender, value);
}
```

## Recommendation
Properly improve the transferFrom() routine so that it is also restricted by the vesting schedule.
