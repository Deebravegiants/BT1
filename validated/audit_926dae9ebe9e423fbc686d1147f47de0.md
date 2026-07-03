Audit Report

## Title
Division-by-Zero in `viewSwapRsETHAmountAndFee` Blocks All Deposits When Rate Is Zero — (`contracts/pools/RSETHPoolV2NBA.sol`)

## Summary
`CrossChainRateReceiver.rate` is a `uint256` that Solidity initialises to `0` and is only updated via `lzReceive()`. `RSETHPoolV2NBA.viewSwapRsETHAmountAndFee()` divides by this rate with no zero-guard, causing every `deposit()` call to revert with a Solidity panic (0x12) for as long as `rate == 0`. This temporarily freezes all deposit functionality.

## Finding Description
`CrossChainRateReceiver` declares `rate` as a plain `uint256` storage variable: [1](#0-0) 

It is written only inside `lzReceive()`: [2](#0-1) 

`getRate()` returns the raw storage value with no zero-check: [3](#0-2) 

`RSETHPoolV2NBA.viewSwapRsETHAmountAndFee()` fetches this rate and uses it as a divisor with no guard: [4](#0-3) 

`deposit()` calls `viewSwapRsETHAmountAndFee()` unconditionally on every invocation: [5](#0-4) 

When `rate == 0`, the expression `amountAfterFee * 1e18 / rsETHToETHrate` triggers a Solidity 0.8.x division-by-zero panic, reverting the entire transaction. No existing check in `deposit()`, `viewSwapRsETHAmountAndFee()`, or `getRate()` guards against a zero rate.

## Impact Explanation
All `deposit()` calls revert for the entire duration that `rate == 0`. Users cannot exchange ETH for wrsETH. This matches **Medium — Temporary freezing of funds**: the deposit flow is completely unavailable, and the freeze lifts only once a valid rate is delivered via `lzReceive()`.

## Likelihood Explanation
The condition is deterministic and guaranteed on every fresh deployment: `rate` starts at `0` and the pool is unusable until the first successful LayerZero cross-chain message arrives. Any LayerZero delivery delay, endpoint misconfiguration, wrong `srcChainId`, or wrong `rateProvider` extends the freeze. No unprivileged action can unblock deposits; only a valid LZ message or an admin call to `setRSETHOracle()` pointing at a pre-seeded oracle resolves it. Any ordinary user attempting to deposit during this window triggers the revert.

## Recommendation
Add a zero-rate guard in `viewSwapRsETHAmountAndFee()`:

```solidity
require(rsETHToETHrate > 0, "Rate not initialised");
```

Alternatively, revert in `getRate()` if `rate == 0`, or reject a zero-value payload inside `lzReceive()` before writing to storage.

## Proof of Concept

```solidity
function testDepositRevertsWhenRateIsZero() public {
    // Deploy receiver — rate defaults to 0
    RSETHRateReceiver receiver = new RSETHRateReceiver(
        srcChainId, address(provider), address(lzEndpoint)
    );

    // Deploy pool pointing at the receiver as oracle
    RSETHPoolV2NBA pool = new RSETHPoolV2NBA();
    pool.initialize(admin, bridger, address(wrsETH), 10, address(receiver));

    // rate == 0 → deposit reverts with Panic(0x12)
    vm.expectRevert();
    pool.deposit{value: 1 ether}("ref");

    // Deliver a valid rate via lzReceive
    bytes memory payload = abi.encode(uint256(1.05e18));
    vm.prank(address(lzEndpoint));
    receiver.lzReceive(srcChainId, abi.encodePacked(address(provider)), 0, payload);

    // Now deposit succeeds
    pool.deposit{value: 1 ether}("ref");
}
```

### Citations

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L13-13)
```text
    uint256 public rate;
```

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L93-95)
```text
        uint256 _rate = abi.decode(_payload, (uint256));

        rate = _rate;
```

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L103-105)
```text
    function getRate() external view returns (uint256) {
        return rate;
    }
```

**File:** contracts/pools/RSETHPoolV2NBA.sol (L111-111)
```text
        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
```

**File:** contracts/pools/RSETHPoolV2NBA.sol (L129-132)
```text
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```
