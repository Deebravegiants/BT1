# [M] Bypass `userWithdrawLimitPerPeriod` check

## Summary
Severity: Medium
Contest weight: 0.6123
Dataset id: 17286
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability consists of a per‑period withdrawal limit that is enforced only against the address that initiates the withdraw call. The contract records how much each address has withdrawn during the current period (userToAmountWithdrawnThisPeriod) and compares it with a fixed cap (userWithdrawLimitPerPeriod). Because the limit is tied to the caller’s address, an attacker can split his holdings across multiple addresses and withdraw the full amount from each address in the same period. The root cause is that the accounting of withdrawn funds does not follow the logical user identity; it relies solely on msg.sender and does not consider token transfers that move balance between accounts. An exploit proceeds as follows: a user deposits a large amount, calls the withdraw function and extracts the maximum allowed amount (for example 1,000 tokens). The contract updates the per‑address counter and blocks any further withdrawal from that address for the remainder of the period. The user then transfers the remaining balance (the other 1,000 tokens) to a second address that has not withdrawn anything yet. Because the limit check in the withdraw hook is performed against the new address, the contract sees a fresh counter of zero and permits another full‑limit withdrawal, effectively allowing the user to extract more than the intended per‑period total. From the user’s perspective the UI may show that the withdrawal limit has been reached for the first account, but the funds are still available after a simple transfer, leading to a mismatch between the displayed limit and the actual amount that can be taken. The impact is that the protocol’s economic safeguards are bypassed, potentially draining funds, breaking accounting assumptions, and allowing malicious actors to exceed rate‑limiting protections. The issue was discovered during a security audit that exercised the withdraw path together with token transfers and observed that the limit counter was not shared across accounts. It can be hard to notice because the transfer function appears benign and the limit check is only present in the withdraw hook, giving the impression that the limit is globally enforced. To remediate, the contract should track the total withdrawn amount per logical user across all addresses, or restrict transfers of withdraw‑eligible balances, or only allow a transfer of the remaining unused limit. In conceptual terms the fix requires moving the limit enforcement from an address‑scoped check to a user‑scoped or global period counter, ensuring that moving tokens does not reset the withdrawal quota.

## Proof of Concept
1. Assume `userWithdrawLimitPerPeriod` is set to `1000`
2. User A has current deposit of amount `2000` and wants to withdraw everything instantly
3. User A calls the withdraw function and takes out the `1000` amount

```solidity
function withdraw(uint256 _amount) external override nonReentrant {
    uint256 _baseTokenAmount = (_amount * baseTokenDenominator) / 1e18;
    uint256 _fee = (_baseTokenAmount * withdrawFee) / FEE_DENOMINATOR;
    if (withdrawFee > 0) { require(_fee > 0, "fee = 0"); }
    else { require(_baseTokenAmount > 0, "amount = 0"); }
    _burn(msg.sender, _amount);
    uint256 _baseTokenAmountAfterFee = _baseTokenAmount - _fee;
    if (address(withdrawHook) != address(0)) {
      baseToken.approve(address(withdrawHook), _fee);
      withdrawHook.hook(msg.sender, _baseTokenAmount, _baseTokenAmountAfterFee);
      baseToken.approve(address(withdrawHook), 0);
    }
    baseToken.transfer(msg.sender, _baseTokenAmountAfterFee);
    emit Withdraw(msg.sender, _baseTokenAmountAfterFee, _fee);
}
```

4. Remaining `1000` amount cannot be withdrawn since `userWithdrawLimitPerPeriod` is reached

```solidity
function hook(
    address _sender,
    uint256 _amountBeforeFee,
    uint256 _amountAfterFee
) external override onlyCollateral {
...
require(userToAmountWithdrawnThisPeriod[_sender] + _amountBeforeFee <= userWithdrawLimitPerPeriod, "user withdraw limit exceeded");
...
}
```

5. User simply transfers his balance to his other account and withdraw from that account
6. Since withdraw limit is tied to account, this new account will be allowed to make withdrawal thus bypassing `userWithdrawLimitPerPeriod`

## Recommendation
User should only be allowed to transfer leftover limit. For example if User already utilized limit X then he should only be able to transfer `userWithdrawLimitPerPeriod-X`.
