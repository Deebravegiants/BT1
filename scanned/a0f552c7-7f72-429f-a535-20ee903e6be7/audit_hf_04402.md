# [M] `BalancerOracle::update

## Summary
Severity: Medium
Contest weight: 0.3288
Dataset id: 21737
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in the price‑oracle update routine of a Balancer‑based contract. When the elapsed time since the last price refresh exceeds the configured updateWaitWindow, the update() function is invoked. Inside this function the code first checks that the waiting period has passed, then immediately copies the variable currentPrice into safePrice and records the current block timestamp as lastUpdate. Only after these assignments does the routine recompute currentPrice by aggregating token prices and pool invariants. Because safePrice is set before the fresh price calculation, it retains the price that was valid at the previous update – a stale value that may be minutes or hours old depending on how long the update was delayed. Consequently, any downstream logic that relies on safePrice (for example slippage checks, collateral valuation, or user‑visible price feeds) will operate on outdated data. This can cause users to receive incorrect quotes, experience unexpected losses, or see their balances appear unchanged while the market moves. The issue manifests whenever an update is triggered after the waiting window, especially if the call is delayed beyond a single window, leading to a price that is effectively two windows old. All participants that depend on the oracle – traders, liquidity providers, and the protocol itself – are affected. The flaw was discovered during a manual audit that inspected the ordering of state updates and noted that the safePrice assignment uses the pre‑computed currentPrice rather than the newly calculated one. The problem is subtle because the contract does emit a new currentPrice, so a superficial check may suggest the oracle is up‑to‑date, while the value actually used for safety checks remains stale. To remediate, the logic should first compute the fresh currentPrice, then assign safePrice = currentPrice and finally update lastUpdate, ensuring that the safe price always reflects the most recent market data. This class of bug is a stale‑data or time‑of‑check‑time‑of‑use (TOCTOU) ordering error in oracle update mechanisms, violating the fundamental accounting assumption that price feeds are current at the moment they are recorded and used.

## Proof of Concept
In the `update()` function these are the lines we’ll find:
    
        //@audit let's say price is out of date and its getting updated won't it get the price from one hour ago?
        //problem is it uses a current timestamp but with an hour old price
                if (block.timestamp - lastUpdate < updateWaitWindow) revert BalancerOracle__update_InUpdateWaitWindow();
                // update the safe price first
                safePrice = safePrice_ = currentPrice;
                lastUpdate = block.timestamp;
    
                uint256[] memory weights = IWeightedPool(pool).getNormalizedWeights();
                uint256 totalSupply = IWeightedPool(pool).totalSupply();
    
                uint256 totalPi = WAD;
                uint256[] memory prices = new uint256[](weights.length);
                // update balances in 18 decimals
                for (uint256 i = 0; i < weights.length; i++) {
                    // reverts if the price is invalid or stale
                    prices[i] = _getTokenPrice(i);
                    uint256 val = wdiv(prices[i], weights[i]);
                    uint256 indivPi = uint256(wpow(int256(val), int256(weights[i])));
    
                    totalPi = wmul(totalPi, indivPi);
                }
    
                currentPrice = wdiv(wmul(totalPi, IWeightedPool(pool).getInvariant()), totalSupply);

From the code, we can see that the `currentPrice` is the last thing updated.

Whenever the `updateWindow` reaches or passes for us to fetch a new price, the `safePrice` is updated first, which is the value from the `lastUpdate` which is “stale”.

It can be argued that its a design decision meaning the `updateWindow` is just time it needs to fetch a new price, but it doesn’t mean the price is old. However, the `updateWindow` can be passed and not updated right after meaning the price is two times back because it wasn’t updated right away.

## Recommendation
Revisit the logic to be able to fetch fresh price whenever there need to be a new price fetched.
