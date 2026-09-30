# [M] `getUnderlyingPrice`

## Summary
Severity: Medium
Contest weight: 0.6317
Dataset id: 16770
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability lies in the price‑oracle interface used by the lending protocol’s Comptroller. The Comptroller is designed to call `oracle.getUnderlyingPrice` and interpret a return value of zero as an error condition, following the Compound convention where the oracle never reverts but signals failure by returning 0. In the current implementation, however, the oracle functions can revert on failure. For example, `getUnderlyingPrice` invokes `getPriceLP`, which calls `sampleSupply`. `sampleSupply` contains a `require` that checks whether enough historic observations exist; if the condition is not met, the function throws with the message "PAIR::NOT READY FOR PRICING". The revert bubbles up to the Comptroller, which is not prepared to handle an exception and consequently aborts the entire transaction. This mismatch between expected non‑reverting behavior and actual reverting logic constitutes an error‑handling bug, a class of issues where a contract violates the contract‑level error protocol. The root cause is the absence of defensive coding – there is no `try/catch` or fallback return of zero when an internal call fails, and internal helper functions assume preconditions that may not hold in production. An attacker could trigger the revert deliberately by supplying a token whose price‑calculation path depends on insufficient LP data, thereby causing the Comptroller’s price‑fetch to fail and freezing borrowing, redeeming, or liquidation actions for that market. Legitimate users would experience symptoms such as transactions that suddenly revert with no clear reason, UI components displaying a price of 0 or failing to show any price, or an inability to borrow or withdraw funds despite sufficient collateral. The impact is medium: normal protocol operation is disrupted, user confidence erodes, and funds may become temporarily inaccessible, though the assets themselves are not stolen. The issue was discovered during a manual audit and code review, where the auditor noted that the oracle’s error‑signalling contract does not match the Comptroller’s expectations. It is easy to miss because a revert appears as a generic transaction failure, and developers may assume that internal functions always succeed. The proper remediation is to wrap calls to external or internal price‑fetching functions in `try/catch` blocks, return a zero price when an error occurs, and ensure that auxiliary functions such as `sampleSupply` handle edge cases without reverting, for example by returning a default value or by checking observation length before proceeding. Aligning the oracle’s behavior with the Comptroller’s contract‑level error handling restores protocol stability and prevents unintended transaction failures.

## Proof of Concept
```solidity
function getUnderlyingPrice(CToken ctoken) external override view returns(uint) {
    address underlying;
    { //manual scope to pop symbol off of stack
        string memory symbol = ctoken.symbol();
        if (compareStrings(symbol, "cCANTO")) {
            underlying = address(wcanto);
            return getPriceNote(address(wcanto), false);
        } else {
            underlying = address(ICErc20(address(ctoken)).underlying()); // We are getting the price for a CErc20 lending market
        }
        //set price statically to 1 when the Comptroller is retrieving Price
        if (compareStrings(symbol, "cNOTE")) { // note in terms of note will always be 1 
            return 1e18; // Stable coins supported by the lending market are instantiated by governance and their price will always be 1 note
        } 
        else if (compareStrings(symbol, "cUSDT") && (msg.sender == Comptroller)) {
            uint decimals = erc20(underlying).decimals();
            return 1e18 * 1e18 / (10 ** decimals); //Scale Price as a mantissa to maintain precision in comptroller
        } 
        else if (compareStrings(symbol, "cUSDC") && (msg.sender == Comptroller)) {
            uint decimals = erc20(underlying).decimals();
            return 1e18 * 1e18 / (10 ** decimals); //Scale Price as a mantissa to maintain precision in comptroller
        }
    }
    
    if (isPair(underlying)) { // this is an LP Token
        return getPriceLP(IBaseV1Pair(underlying));
    }
    // this is not an LP Token
    else {
        if (isStable[underlying]) {
            return getPriceNote(underlying, true); // value has already been scaled
        }

        return getPriceCanto(underlying) * getPriceNote(address(wcanto), false) / 1e18;
    }   
}
```

The `Comptroller` is expecting `oracle.getUnderlyingPrice` to return `0` for errors (Compound style returns, no revert).

However, the current implementation will revert when errored:

```solidity
function getPriceLP(IBaseV1Pair pair) internal view returns(uint) {
    uint[] memory supply = pair.sampleSupply(8, 1);
    uint[] memory prices; 
    uint[] memory unitReserves; 
    uint[] memory assetReserves; 
    address token0 = pair.token0();
    address token1 = pair.token1();
    uint decimals;
}

function sampleSupply(uint points, uint window) public view returns (uint[] memory) {
    uint[] memory _totalSupply = new uint[](points);
    
    uint lastIndex = observations.length-1;
    require(lastIndex >= points * window, "PAIR::NOT READY FOR PRICING");
    uint i = lastIndex - (points * window); // point from which to begin the sample
    uint nextIndex = 0;
    uint index = 0;
    uint timeElapsed;

    for(; i < lastIndex; i+=window) {
        nextIndex = i + window;
        timeElapsed = observations[nextIndex].timestamp - observations[i].timestamp;
        _totalSupply[index] = (observations[nextIndex].totalSupplyCumulative - observations[i].totalSupplyCumulative) / timeElapsed;
        index = index + 1;
    }

    return _totalSupply;
}
```

## Recommendation
Consider using `try catch` and return 0 when errored.
