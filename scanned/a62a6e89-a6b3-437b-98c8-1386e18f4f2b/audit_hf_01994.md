# [M] Verify pool legitimacy

## Summary
Severity: Medium
Contest weight: 0.4599
Dataset id: 11201
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The constructor in OverlayV1UniswapV3Factory.sol and OverlayV1UniswapV3Feed.sol only does a partial check to see if the pool corresponds to the supplied tokens. This is accomplished by calling the pool’s functions but if the pool were to be malicious, it could return any token. Additionally, checks can be bypassed by supplying the same tokens twice. Because the deployFeed() function is permissionless, it is possible to deploy malicious feeds. Luckily, the deployMarket() function is permissioned and prevents malicious markets from being deployed.
```solidity
contract OverlayV1UniswapV3Factory is IOverlayV1UniswapV3FeedFactory, OverlayV1FeedFactory {
    constructor(address _ovlWethPool, address _ovl, ...) {
        ovlWethPool = _ovlWethPool; // no check on validity of _ovlWethPool here
        ovl = _ovl;
    }

    function deployFeed(address marketPool, address marketBaseToken, address marketQuoteToken, ...)
        external returns (address feed_) { // Permissionless
        ... // no check on validity of marketPool here
    }
}

contract OverlayV1UniswapV3Feed is IOverlayV1UniswapV3Feed, OverlayV1Feed {
    constructor(
        address _marketPool,
        address _ovlWethPool,
        address _ovl,
        address _marketBaseToken,
        address _marketQuoteToken,
        ... ) ... {
        ...
        address _marketToken0 = IUniswapV3Pool(_marketPool).token0(); // relies on a valid _marketPool
        address _marketToken1 = IUniswapV3Pool(_marketPool).token1();
        require(_marketToken0 == WETH || _marketToken1 == WETH, "OVLV1Feed: marketToken != WETH");
        marketToken0 = _marketToken0;
        marketToken1 = _marketToken1;
        require(
            _marketToken0 == _marketBaseToken || _marketToken1 == _marketBaseToken,
            "OVLV1Feed: marketToken != marketBaseToken"
        );
        require(
            _marketToken0 == _marketQuoteToken || _marketToken1 == _marketQuoteToken,
            "OVLV1Feed: marketToken != marketQuoteToken"
        );
        marketBaseToken = _marketBaseToken; // what if _marketBaseToken == _marketQuoteToken == WETH ?
        marketQuoteToken = _marketQuoteToken;
        marketBaseAmount = _marketBaseAmount;
        // need OVL/WETH pool for ovl vs ETH price to make reserve conversion from ETH => OVL
        address _ovlWethToken0 = IUniswapV3Pool(_ovlWethPool).token0(); // relies on a valid _ovlWethPool
        address _ovlWethToken1 = IUniswapV3Pool(_ovlWethPool).token1();
        require(
            _ovlWethToken0 == WETH || _ovlWethToken1 == WETH,
            "OVLV1Feed: ovlWethToken != WETH"
        );
        require(
            _ovlWethToken0 == _ovl || _ovlWethToken1 == _ovl, // What if _ovl == WETH ?
            "OVLV1Feed: ovlWethToken != OVL"
        );
        ovlWethToken0 = _ovlWethToken0;
        ovlWethToken1 = _ovlWethToken1;
        marketPool = _marketPool;
        ovlWethPool = _ovlWethPool;
        ovl = _ovl;
    }
```

## Recommendation
Verify that pools are indeed Uniswap pools and the supplied tokens do generate the supplied pool.
