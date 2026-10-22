# [M] `ConcentratedLiquidityPoolHelper`: `getTickState

## Summary
Severity: Medium
Contest weight: 0.3791
Dataset id: 943
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in the public view function getTickState of the ConcentratedLiquidityPoolHelper contract. This routine attempts to return the state of every tick that has been inserted into a pool, including the sentinel MIN_TICK and MAX_TICK values. The implementation walks the linked‑list of ticks by starting at the first tick and iterating until it reaches the maximum tick, copying each tick’s index and liquidity into a dynamic array. Because the function does not impose a hard limit on the number of iterations and does not allow callers to specify a pagination window, the loop can grow arbitrarily large depending on the pool’s tick spacing and the total number of active ticks. When the number of ticks becomes sufficiently high, the gas required to execute the loop exceeds the block gas limit, causing the call to run out of gas and revert. This situation can be triggered unintentionally by a pool that simply has a dense distribution of ticks, or maliciously by an adversary who creates or expands a pool with many ticks to make the function unusable. From a user’s perspective the contract appears to return no data or the transaction fails, even though the caller only expected to read information; the UI may display an empty list, a timeout, or an error message where a full tick state was expected. No ether or tokens are directly lost, but the denial‑of‑service effect prevents developers, front‑ends, and analytics tools from retrieving essential pricing and liquidity information, breaking assumptions about the availability of on‑chain accounting data. The issue was identified during a Code4rena audit, where reviewers noted that the function’s gas consumption scales linearly with the number of ticks and therefore can become prohibitive. The problem is subtle because view functions are often assumed to be cheap, and the gas exhaustion only manifests under specific configurations, making it easy to overlook during ordinary testing. The flaw belongs to the broader class of unbounded iteration or gas‑limit DoS bugs. To remediate the issue, the function should be redesigned to accept a start index and a maximum count (or similar pagination parameters) and to respect the pool’s tickCount field, thereby limiting the number of ticks processed per call. This change allows callers to request the tick state in manageable chunks, ensuring that gas usage stays within reasonable bounds and that the contract’s informational API remains reliable.

## Recommendation
Have a starting index parameter to start the iteration from. Also, `tickCount` can be made use of more meaningfully to limit the number of iterations performed.
    
```solidity
function getTickState(
    IConcentratedLiquidityPool pool,
    int24 startIndex,
    uint24 tickCount
) external view returns (SimpleTick[] memory) {
    SimpleTick[] memory ticks = new SimpleTick[](tickCount);

    IConcentratedLiquidityPool.Tick memory tick;
    int24 current = startIndex;

    for (uint24 i; i < tickCount; i++) {
        tick = pool.ticks(current);
        ticks[i] = SimpleTick({index: current, liquidity: tick.liquidity});
        // reached end of linked list, exit loop
        if (current == TickMath.MAX_TICK) break;
        // else, continue with next iteration
        current = tick.nextTick;
    }

    return ticks;
}
```

Functionality is affected, severity 2.
