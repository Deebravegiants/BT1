# [H] Ineffective ReserveRatio Enforcement

## Summary
Severity: High
Chain: Smart contract
Component: 2022-05-rubicon
Published: 2022-05-27
Source: https://github.com/code-423n4/2022-05-rubicon-findings/issues/106
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-05-rubicon/blob/8c312a63a91193c6a192a9aab44ff980fbfd7741/contracts/rubiconPools/BathPair.sol#L324
https://github.com/code-423n4/2022-05-rubicon/blob/8c312a63a91193c6a192a9aab44ff980fbfd7741/contracts/rubiconPools/BathPair.sol#L160


# Vulnerability details

## Background

Per whitepaper, ReserveRatio ensures that some amount of pool liquidity is present in the contract at all times. This protects the pools from overutilization by strategists and ensures that a portion of the underlying pool assets are liquid so LPs can withdraw. If the ReserveRatio is set to 50, meaning 50% of a liquidity pool’s assets must remain in the pool at all times.

However, it was possible for the strategists to bypass the Reserve Ratio restriction and utilize all the funds in the pools, causing the pools to be illiquid.

## Proof-of-Concept

Strategists place their market making trades via the  `BathPair.placeMarketMakingTrades` function. This function would first checks if the pool's reserveRatio is maintained before proceeding. If true, strategists will be allowed to place their market making trades with orders with arbitrary pay amount. Strategists could place ask and bid orders with large pay amount causing large amount of funds will be withdrawen from the pools. The root cause is that at the end of the transaction, there is no additional validation to ensure the pools are not overutilization by strategists and the reserve ratio of the pools is maintained.

[https://github.com/code-423n4/2022-05-rubicon/blob/8c312a63a91193c6a192a9aab44ff980fbfd7741/contracts/rubiconPools/BathPair.sol#L324](https://github.com/code-423n4/2022-05-rubicon/blob/8c312a63a91193c6a192a9aab44ff980fbfd7741/contracts/rubiconPools/BathPair.sol#L324)

```solidity
function placeMarketMakingTrades(
    address[2] memory tokenPair, // ASSET, Then Quote
    uint256 askNumerator, // Quote / Asset
    uint256 askDenominator, // Asset / Quote
    uint256 bidNumerator, // size in ASSET
    uint256 bidDenominator // size in QUOTES
) public onlyApprovedStrategist(msg.sender) returns (uint256 id) {
    // Require at least one order is non-zero
    require(
        (askNumerator > 0 && askDenominator > 0) ||
            (bidNumerator > 0 && bidDenominator > 0),
        "one order must be non-zero"
    );

    address _underlyingAsset = tokenPair[0];
    address _underlyingQuote = tokenPair[1];

    (
        address bathAssetAddress,
        address bathQuoteAddress
    ) = enforceReserveRatio(_underlyingAsset, _underlyingQuote);

    require(
        bathAssetAddress != address(0) && bathQuoteAddress != address(0),
        "tokenToBathToken error"
    );
    .. SNIP..
    // Place new bid and/or ask
    // Note: placeOffer returns a zero if an incomplete order
    uint256 newAskID = IBathToken(bathAssetAddress).placeOffer(
        ask.pay_amt,
        ask.pay_gem,
        ask.buy_amt,
        ask.buy_gem
    );

    uint256 newBidID = IBathToken(bathQuoteAddress).placeOffer(
        bid.pay_amt,
        bid.pay_gem,
        bid.buy_amt,
        bid.buy_gem
    );
    .. SNIP..
}
```

[https://github.com/code-423n4/2022-05-rubicon/blob/8c312a63a91193c6a192a9aab44ff980fbfd7741/contracts/rubiconPools/BathPair.sol#L160](https://github.com/code-423n4/2022-05-rubicon/blob/8c312a63a91193c6a192a9aab44ff980fbfd7741/contracts/rubiconPools/BathPair.sol#L160)

```solidity
/// @notice This function enforces that the Bath House reserveRatio (a % of underlying pool liquidity) is enforced across all pools
/// @dev This function should ensure that reserveRatio % of the underlying liquidity always remains on the Bath Token. Utilization should be 1 - reserveRatio in practice assuming strategists use all available liquidity.
function enforceReserveRatio(
    address underlyingAsset,
    address underlyingQuote
)
    internal
    view
    returns (address bathAssetAddress, address bathQuoteAddress)
{
    bathAssetAddress = IBathHouse(bathHouse).tokenToBathToken(
        underlyingAsset
    );
    bathQuoteAddress = IBathHouse(bathHouse).tokenToBathToken(
        underlyingQuote
    );
    require(
        (
            IBathToken(bathAssetAddress).underlyingBalance().mul(
                IBathHouse(bathHouse).reserveRatio()
            )
        ).div(100) <= IERC20(underlyingAsset).balanceOf(bathAssetAddress),
        "Failed to meet asset pool reserve ratio"
    );
    require(
        (
            IBathToken(bathQuoteAddress).underlyingBalance().mul(
                IBathHouse(bathHouse).reserveRatio()
            )
        ).div(100) <= IERC20(underlyingQuote).balanceOf(bathQuoteAddress),
        "Failed to meet quote pool reserve ratio"
    );
}
```

## Test Cases

The following is the snippet of the test case result. Reserve Ratio is initialized to 80% in this example, which means only 20% of the funds could be utilized by strategists. The BathWETH and BathDAI pools contained 1 WETH and 100 DAI respectively after users deposited their funds into the pools. At the bottom half of the output, it shows that it was possible for the strategists could utilised 90% of the funds in the pools to place an ask and bid order, which exceeded the 20% limit.

The last two lines of the output show that 90% of the funds in the pools are outstanding.

```solidity
..SNIP..
--------------- Order Book ---------------
[-] asks index 0: ask_pay_amt = 0, ask_buy_amt = 0
[-] asks index 1: ask_pay_amt = 0, ask_buy_amt = 0
[-] asks index 2: ask_pay_amt = 0, ask_buy_amt = 0
[-] asks index 3: ask_pay_amt = 0, ask_buy_amt = 0
[+] bids index 0: bid_pay_amt = 0, bid_buy_amt = 0
[+] bids index 1: bid_pay_amt = 0, bid_buy_amt = 0
[+] bids index 2: bid_pay_amt = 0, bid_buy_amt = 0
[+] bids index 3: bid_pay_amt = 0, bid_buy_amt = 0
bathAssetInstance: underlyingBalance() = 1 WETH, balanceOf = 1 WETH, Outstanding Amount = 0 WETH
bathQuoteInstance: underlyingBalance() = 100 DAI, balanceOf = 100 DAI, Outstanding Amount = 0 DAI
After Placing Order
--------------- Order Book ---------------
[-] asks index 0: ask_pay_amt = 0.9, ask_buy_amt = 180
[-] asks index 1: ask_pay_amt = 0, ask_buy_amt = 0
[-] asks index 2: ask_pay_amt = 0, ask_buy_amt = 0
[-] asks index 3: ask_pay_amt = 0, ask_buy_amt = 0
[+] bids index 0: bid_pay_amt = 90, bid_buy_amt = 0.9
[+] bids index 1: bid_pay_amt = 0, bid_buy_amt = 0
[+] bids index 2: bid_pay_amt = 0, bid_buy_amt = 0
[+] bids index 3: bid_pay_amt = 0, bid_buy_amt = 0
bathAssetInstance: underlyingBalance() = 1 WETH, balanceOf = 0.1 WETH, Outstanding Amount = 0.9 WETH
bathQuoteInstance: underlyingBalance() = 100 DAI, balanceOf = 10 DAI, Outstanding Amount = 90 DAI
..SNIP..
```

Test Script can be found at [https://gist.github.com/xiaoming9090/c4fcd4e967bd7d6940429e5d8e39004d](https://gist.github.com/xiaoming9090/c4fcd4e967bd7d6940429e5d8e39004d)

## Impact

Following are the impacts of this issue:

1. Underlying pool assets are overutilization by strategists, causing the pools to be illiquid. Users might not be able to withdraw their funds from the pools as the pools might not have sufficient underlying assets remained as their assets have been deploy to the Rubicon Market

2. Reserve Ratio is one of the key security parameters to safeguard LP's funds so that the amount of losses the pools could potentially incur is limited. Without effective reserve ratio enforcement, strategists could deploy ("invest") all the user capital on the Rubicon Market. If the strategist makes a loss from all their orders, the LP would incur significant loss.

## Recommended Mitigation Steps

Check that the reserveRatio for each of the underlying liquidity pools (asset and quote bathTokens) is observed before and after function execution.

```solidity
function placeMarketMakingTrades(
    address[2] memory tokenPair, // ASSET, Then Quote
    uint256 askNumerator, // Quote / Asset
    uint256 askDenominator, // Asset / Quote
    uint256 bidNumerator, // size in ASSET
    uint256 bidDenominator // size in QUOTES
) public onlyApprovedStrategist(msg.sender) returns (uint256 id) {
    // Require at least one order is non-zero
    require(
        (askNumerator > 0 && askDenominator > 0) ||
            (bidNumerator > 0 && bidDenominator > 0),
        "one order must be non-zero"
    );

    address _underlyingAsset = tokenPair[0];
    address _underlyingQuote = tokenPair[1];

    (
        address bathAssetAddress,
        address bathQuoteAddress
    ) = enforceReserveRatio(_underlyingAsset, _underlyingQuote);

    require(
        bathAssetAddress != address(0) && bathQuoteAddress != address(0),
        "tokenToBathToken error"
    );
    .. SNIP..
    // Place new bid and/or ask
    // Note: placeOffer returns a zero if an incomplete order
    uint256 newAskID = IBathToken(bathAssetAddress).placeOffer(
        ask.pay_amt,
        ask.pay_gem,
        ask.buy_amt,
        ask.buy_gem
    );

    uint256 newBidID = IBathToken(bathQuoteAddress).placeOffer(
        bid.pay_amt,
        bid.pay_gem,
        bid.buy_amt,
        bid.buy_gem
    );
    .. SNIP..

    // Ensure that the strategist does not overutilize
    enforceReserveRatio(_underlyingAsset, _underlyingQuote);
}
```
