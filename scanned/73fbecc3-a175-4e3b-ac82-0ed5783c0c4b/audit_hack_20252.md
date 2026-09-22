# [M] 5.2.2 Verify pool legitimacy

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk
**Context:** OverlayV1UniswapV3Factory.sol#L19-L40, OverlayV1UniswapV3Feed.sol#L30-L
**Description:** TheconstructorinOverlayV1UniswapV3Factory.solandOverlayV1UniswapV3Feed.solonly
does a partial check to see if the pool corresponds to the supplied tokens. This is accomplished by calling the
pool’s functions but if the pool were to be malicious, it could return any token. Additionally, checks can be by-
passed by supplying the same tokens twice.
Because thedeployFeed()function is permissionless, it is possible to deploy malicious feeds. Luckily, thede-
ployMarket()function is permissioned and prevents malicious markets from being deployed.
contract OverlayV1UniswapV3Factory is IOverlayV1UniswapV3FeedFactory, OverlayV1FeedFactory {
constructor(address _ovlWethPool, address _ovl, ...) {
ovlWethPool = _ovlWethPool;// no check on validity of _ovlWethPool here
ovl = _ovl;
}
function deployFeed(address marketPool, address marketBaseToken, address marketQuoteToken, ...)
external returns (address feed_) {// Permissionless
...// no check on validity of marketPool here
}


```
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
address _marketToken0 = IUniswapV3Pool(_marketPool).token0();// relies on a valid _marketPool
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
marketBaseToken = _marketBaseToken;// what if _marketBaseToken == _marketQuoteToken == WETH?
marketQuoteToken = _marketQuoteToken;
marketBaseAmount = _marketBaseAmount;
// need OVL/WETH pool for ovl vs ETH price to make reserve conversion from ETH => OVL
address _ovlWethToken0 = IUniswapV3Pool(_ovlWethPool).token0();// relies on a valid
,! _ovlWethPool
address _ovlWethToken1 = IUniswapV3Pool(_ovlWethPool).token1();
require(
_ovlWethToken0 == WETH || _ovlWethToken1 == WETH,
"OVLV1Feed: ovlWethToken != WETH"
);
require(
_ovlWethToken0 == _ovl || _ovlWethToken1 == _ovl,// What if _ovl == WETH?
"OVLV1Feed: ovlWethToken != OVL"
);
ovlWethToken0 = _ovlWethToken0;
ovlWethToken1 = _ovlWethToken1;
marketPool = _marketPool;
ovlWethPool = _ovlWethPool;
ovl = _ovl;
}
```
**Recommendation:** Verify that pools are indeed Uniswap pools and the supplied tokens do generate the supplied
pool.
Note: Verifying that a legitimate Uniswap pool is used still allows for the possibility of malicious tokens making it
into the pool.
Consider changing thedeployFeed()function to be permissioned the same waydeployMarket()also is.
When deploying a market viadeployMarket()make sure only valid feeds and tokens are used.
Consider checking the pools using the example code below, note that:


- This can be done for both themarketPooland the_ovlWethPool
- Determine where to do this, inOverlayV1UniswapV3Factoryand/orOverlayV1UniswapV3Feed
- This way the pool address doesn’t even have to be supplied.
- You have to supply a fee togetPool(). It seems only 3 fees used.
IUniswapV3Factory constant UniswapV3Factory =
,! IUniswapV3Factory(address(0x1F98431c8aD98523631AE4a59f267346ea31F984));
uint24[3] memory FeeAmount=[uint24(500),uint24(3000),uint24(10000)];
for (uint i=0;i<FeeAmount.length;i++) {
pool = UniswapV3Factory.getPool(token1,token2,FeeAmount[i]);
if (pool != address(0)) break;
}

**Overlay:** Fixed in commit b889200.
**Spearbit:** Acknowledged.
