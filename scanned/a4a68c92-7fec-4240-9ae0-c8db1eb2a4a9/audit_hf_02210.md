# [C] Option Pool Draining With Invalid optionType

## Summary
Severity: Critical
Contest weight: 0.7860
Dataset id: 12225
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Hegic options are created with four required elements, i.e., period, amount, strike, and optionType.
These four elements are essential in calculating respective fees (e.g., premium, locked assets, and
settlement fee) and then introducing a new option into the protocol.
To elaborate, we show below the create() routine of the HegicETHOptions contract. Note this
routine performs a number of sanity checks, including the option periods as well as related fee
requirements. However, it does not validate the last parameter optionType. With that, a malicious
actor could potentially craft a new option with an invalid optionType to drain all available funds in
the pool.
```solidity
function create(
    uint256 period,
    uint256 amount,
    uint256 strike,
    OptionType optionType
) external payable returns (uint256 optionID) {
    (uint256 total, uint256 settlementFee, uint256 strikeFee,) = fees(
        period,
        amount,
        strike,
        optionType
    );
    require(period >= 1 days, "Period is too short");
    require(period <= 4 weeks, "Period is too long");
    require(amount > strikeFee, "Price difference is too large");
    require(msg.value == total, "Wrong value");
    uint256 strikeAmount = amount.sub(strikeFee);
    optionID = options.length;
    Option memory option = Option(
        State.Active,
        msg.sender,
        strike,
        amount,
        strikeAmount.mul(optionCollateralizationRatio).div(100).add(strikeFee),
        total.sub(settlementFee),
        block.timestamp + period,
        optionType
    );
    options.push(option);
    settlementFeeRecipient.sendProfit{value: settlementFee}();
    pool.lock{value: option.premium}(optionID, option.lockedAmount);
    emit Create(optionID, msg.sender, settlementFee, total);
}
```
Specifically, a malicious actor requests a new option with the four required elements: period
= 1 days, amount = 1 eth, strike = latestPrice*10**18, and optionType = 100. These elements can
successfully pass current sanity checks and result in a new option creation with the following re-
spective fees: settlementFee = 0.1 eth, strikeFee = 0 eth and protocolFee = amount*sqrt(period)*
impliedVolRate/10**26 ~= 0.
After the creation, the crafted option can be immediately exercised and the main logic is im-
plemented in the payProfit() routine (shown below). As the option's optionType is crafted, which
is not OptionType.Call, the routine takes the else branch in lines 314-317. Also, since the strike
price is significantly larger than the latestPrice, the resulting profit (line 316) becomes significantly
larger than the option's locked amount. As a result, the malicious actor can immediately exercise
the crafted option to get back the option's locked amount (line 320).
```solidity
/**
 * @notice Sends profits in ETH from the ETH pool to an option holder's address
 * @param optionID A specific option
 */
function payProfit(uint optionID) internal returns (uint profit) {
    Option memory option = options[optionID];
    (, int latestPrice,) = priceProvider.latestRoundData();
    uint256 currentPrice = uint256(latestPrice);
    if (option.optionType == OptionType.Call) {
        require(option.strike <= currentPrice, "Current price is too low");
        profit = currentPrice.sub(option.strike).mul(option.amount).div(currentPrice);
    } else {
        require(option.strike >= currentPrice, "Current price is too high");
        profit = option.strike.sub(currentPrice).mul(option.amount).div(currentPrice);
    }
    if (profit > option.lockedAmount) profit = option.lockedAmount;
    pool.send(optionID, option.holder, profit);
}
```
To summarize, the actor essentially invests 1% * amount into the option creation, but immediately
gets back the corresponding locked amount, i.e., amount.mul(optionCollateralizationRatio).div(100)
= 50% * amount. By continuing the above process, the actor can drain all funds available in the
current pool. Note both HegicETHOptions and HegicWBTCOptions are affected.

## Recommendation
Validate the given optionType in both pools and prevent invalid ones from
entering the option creation.
