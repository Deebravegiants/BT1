# [H] Any referrer can overwrite other

## Summary
Severity: High
Contest weight: 0.7926
Dataset id: 1762
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Due to wrong access control/wrong design of referral code usage, any referrer can overwrite any other traders' referral codes into their own. This redirects all trading fee rebates to the adversary's account instead of the rightful referrer, and will even cause traders to lose funds due to forced decreased discount.
In Referral, the function setTraderReferralCodeByOwner() allows anyone (any referrer) to overwrite any trader's code into their own code:
```solidity
function setTraderReferralCodeByOwner(bytes32 _code, address _trader) external whenNotPaused {
    require(codeOwners[_code] == msg.sender, "OWNER_ONLY");
}
```
Referral.sol#L170
Anyone can also become a referrer just by registering their own code of choice, as long as they haven't own any:
```solidity
function registerCode(bytes32 _code) external whenNotPaused {
    require(_code != bytes32(0), "Referral: invalid _code");
    require(codeOwners[_code] == address(0), "Referral: code already exists");
    require(codes[msg.sender] == bytes32(0), "Referral: referrer already registered");
    codeOwners[_code] = msg.sender;
    codes[msg.sender] = _code;
    referrerTiers[msg.sender] = _DEFAULT_TIER_ID;
    isPrivate[_code] = false;
    emit RegisterCode(msg.sender, _code);
}
```
Referral.sol#L180
When a trade is opened, the trading fee discount is applied to the trader, and the trading fee rebate is sent to the referrer:
```solidity
function applyReferralAndPnlFee(
    address _trader,
    uint _fees,
    uint _leveragedPosition,
    bool _isPnl,
    uint _pairIndex,
    int _percentProfit,
    uint _collateral
) public override onlyTrading returns (uint, uint) {
    (uint traderFeePostDiscount, address referrer, uint referrerRebate) = referral.traderReferralDiscount(_trader, _fees);
    rebates[referrer] += referrerRebate;
}
```
TradingStorage.sol#L580-L582
The referrer can easily claim the rebate through claimRebate(), without the admin having any power to stop them.
TradingStorage.sol#L649-L656
Internal pre-conditions
None
External pre-conditions
None
Attack Path
1. Alice (whale) deposits a large amount of margin. Alice applies a tier-3 code to get the maximum fee discount of 15%.
2. Bob monitors the mainnet, and sees this activity.
3. Bob creates a new referral code, and overwrites Alice's code into their own with setTraderReferralCodeByOwner(). New referral codes starts at tier 1, given only a 5% discount.
4. When Alice opens a trade, the fee discount/rebate is applied based on Bob's code instead.
If Alice sets back the old code, Bob can simply backrun her to set his new code again.
The end result is that:
• Alice only gets a 5% fee discount, instead of the rightful 15% from Alice's referrer.
• Alice's referrer loses the 15% fee rebate completely. Bob gets a 5% fee rebate from Alice's trade.
• Attacker gets all the trading rebates for themselves. Legit referrers lose that trading rebate.
• Trader is forced a lower fee discount with the attacker's tier-1 referral code, instead of being able to take a higher discount with a tier-3 referral code that the trader wills to.

## Recommendation
Traders should be allowed to decide which referral code they wish to use. There are some possible designs for this:
• Delete setTraderReferralCodeByOwner() entirely. For private codes, a referrer should only be able to invite a trader to use their code. The trader should explicitly accept the invitation to use the code.
• setTraderReferralCodeByOwner() should only be possible if the trader hasn't been applied any referral codes. The trader should be allowed to change code at will, if the current referral code isn't from whom they know.
