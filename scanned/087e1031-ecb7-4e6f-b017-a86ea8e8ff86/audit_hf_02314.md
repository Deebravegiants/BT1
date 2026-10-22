# [M] Gas-Efficient New Pair Deployment

## Summary
Severity: Medium
Contest weight: 0.4601
Dataset id: 12600
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
OneSwap acts as a trustless intermediary between liquidity providers and trading users. The liquidity providers deposit certain amount of stock and money assets into the OneSwap pool and in return get the tokenized pool share of current reserves. Later on, the liquidity providers can withdraw their own share by returning the pool tokens back to the pool. With assets in the pool, users can submit swap or limit orders and the trading price is determined according to the current order book and/or AMM price curve.

When the pool does not exist, the first liquidity provider's addLiquidity() operation will trigger the creation of the pool (via the createPair() function). As the name indicates, createPair() performs necessary sanity checks and then instantiates the pool contract creation (line 60): OneSwapPair oneswap = new OneSwapPair(weth, stock, money, isOnlySwap, uint64(uint(10)**dec), priceMul, priceDiv

```solidity
function createPair(address stock, address money, bool isOnlySwap) external override returns (address pair) {
    require(stock != money, "OneSwapFactory: IDENTICAL_ADDRESSES");
    require(stock != address(0) && money != address(0), "OneSwapFactory: ZERO_ADDRESS");
    uint moneyDec = uint(IERC20(money).decimals());
    uint stockDec = uint(IERC20(stock).decimals());
    require(23 >= stockDec && stockDec >= 0, "OneSwapFactory: STOCK_DECIMALS_NOT_SUPPORTED");
    uint dec = 0;
    if (stockDec >= 4) dec = stockDec - 4; // now 19 >= dec && dec >= 0
    // 10**19 = 10000000000000000000, 1<<64 = 18446744073709551616
    uint64 priceMul = 1;
    uint64 priceDiv = 1;
    bool differenceTooLarge = false;
    if (moneyDec > stockDec) {
        if (moneyDec > stockDec + 19) {
            differenceTooLarge = true;
        } else {
            priceMul = uint64(uint(10) ** (moneyDec - stockDec));
        }
    }
    if (stockDec > moneyDec) {
        if (stockDec > moneyDec + 19) {
            differenceTooLarge = true;
        } else {
            priceDiv = uint64(uint(10) ** (stockDec - moneyDec));
        }
    }
    require(!differenceTooLarge, "OneSwapFactory: DECIMALS_DIFF_TOO_LARGE");
    bytes32 salt = keccak256(abi.encodePacked(stock, money, isOnlySwap));
    require(_tokensToPair[salt] == address(0), "OneSwapFactory: PAIR_EXISTS");
    OneSwapPair oneswap = new OneSwapPair{salt: salt}(weth, stock, money, isOnlySwap, uint64(uint(10) ** dec), priceMul, priceDiv);
    pair = address(oneswap);
    allPairs.push(pair);
    _tokensToPair[salt] = pair;
    _pairWithToken[pair] = TokensInPair(stock, money);
    emit PairCreated(pair, stock, money, isOnlySwap);
}
```

The pair contract is a complicated one and its instantiation inevitably consumes significant amount of gas. Such gas-consuming pool contract deployment would discourage liquidity providers engagement. An alternative would be to explore a proxy-based approach by implementing the pool contract as a logic one. By doing so, we only need to deploy a minimal proxy for each pair, hence lowering the entry barrier for liquidity providers, especially for the creation of trading pools. Recall that in order to prevent the first liquidity provider from monopolizing the liquidity pool, the provider has been penalized by forcibly burning the very first _MINIMUM_LIQUIDITY = 10 ** 3 pool shares. It is just not justifiable to further penalize early liquidity providers who introduce the trading pools into the OneSwap ecosystem!

## Recommendation
Explore the proxy-based approach of deploying pool contracts to lower the barrier for early participation.
