# [C] Arbitrary Setting of User Referral

## Summary
Severity: Critical
Contest weight: 0.6357
Dataset id: 12799
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As mentioned before, the POOP token forks from Openzeppelin's ERC20 template and adds two interfaces, e.g., `buy()` and `sell()`. At the same time, these functions also serve as the interface to set referral address. While review the referral address configuration logic, we notice a critical bug which will allow anyone to set the referral address of any user arbitrarily. To elaborate, we show below the `buy()` routine.
```solidity
function buy(address receiver, address referral) external payable nonReentrant {
    require(START, "not started");
    require(PUBLIC_BUY || whitelist[msg.sender], "illegal caller");
    require(msg.value >= MIN_BUY_AMOUNT && msg.value <= MAX_BUY_AMOUNT, "must trade over min and below max");
    address currentReferral = referrals[receiver];
    if (currentReferral == address(0) && referral != address(0)) {
        referrals[receiver] = referral;
        currentReferral = referral;
        emit ReferralRelation(receiver, referral, block.timestamp);
    }
    if (currentReferral == address(0)) {
        currentReferral = INCENTIVE_VAULT;
    }
    // Mint Poop to sender
    uint256 poop = ETHtoPOOP(msg.value);
    _mint(receiver, (poop * BUY_AFTER_FEE) / FEE_BASE);
    // Reserve fee
    uint value = msg.value;
    if (RESERVE_FEE_ADDRESS != address(0)) {
        sendEth(RESERVE_FEE_ADDRESS, value / RESERVE_FEES);
    }
    // Referral Fee
    if (currentReferral != address(0)) {
        sendEth(currentReferral, value / REFERRAL_FEE);
        emit ReferralReward(receiver, currentReferral, value / REFERRAL_FEE, block.timestamp);
    }
    emit Price(block.timestamp, poop, msg.value);
}
```
It comes to our attention that this routine does not properly handle the validation of `msg.sender` and `receiver`, which will allow any `msg.sender` to set any `referrals[receiver]`. Also, the address can not be changed once configured. As a result, a malicious actor could front run every `buy()` transaction to set the referral address which could make a profit in the `buy()` transaction.

## Recommendation
Revise the `buy()` logic to properly validate `receiver == msg.sender`.
