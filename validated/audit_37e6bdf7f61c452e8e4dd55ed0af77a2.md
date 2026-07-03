### Title
Zero Rate Division-by-Zero in `RSETHPoolV2NBA.viewSwapRsETHAmountAndFee` Temporarily Freezes All Deposits — (`contracts/pools/RSETHPoolV2NBA.sol`)

---

### Summary

`CrossChainRateReceiver.rate` is a `uint256` storage variable that defaults to `0` at deployment and is only updated when a LayerZero cross-chain message arrives via `lzReceive()`. `RSETHPoolV2NBA.viewSwapRsETHAmountAndFee()` divides by this rate with no zero-guard. Any `deposit()` call before the first valid rate update — or after a prolonged LayerZero outage — reverts with a division-by-zero panic, temporarily freezing all deposits.

---

### Finding Description

**Step 1 — Rate starts at zero.**

`CrossChainRateReceiver` declares `rate` as a plain `uint256`: [1](#0-0) 

Solidity initialises it to `0`. It is only written in `lzReceive()`: [2](#0-1) 

`getRate()` returns the raw storage value with no zero-check: [3](#0-2) 

**Step 2 — Pool reads the rate and divides.**

`RSETHPoolV2NBA.viewSwapRsETHAmountAndFee()` fetches the rate and uses it as a divisor: [4](#0-3) 

There is no guard for `rsETHToETHrate == 0`.

**Step 3 — `deposit()` is the public entry point.**

`deposit()` calls `viewSwapRsETHAmountAndFee()` unconditionally: [5](#0-4) 

Any non-zero ETH deposit before the first `lzReceive()` call triggers the division-by-zero panic and reverts.

---

### Impact Explanation

All `deposit()` calls revert with a Solidity division-by-zero panic (0x12) for as long as `rate == 0`. This is a **temporary freeze of user funds in transit** — users cannot exchange ETH for wrsETH. The freeze lifts automatically once a valid rate is delivered via `lzReceive()`. Impact: **Medium — Temporary freezing of funds**.

---

### Likelihood Explanation

The window is deterministic and guaranteed:

- Every fresh deployment of `RSETHRateReceiver` starts with `rate = 0`.
- The pool is usable only after the first successful cross-chain rate push from `RSETHRateProvider.updateRate()`.
- Any LayerZero delivery delay, outage, or misconfiguration (wrong `srcChainId`, wrong `rateProvider`) extends the freeze indefinitely.
- No admin action can unblock deposits without either (a) delivering a valid LZ message or (b) pointing the pool at a different oracle via `setRSETHOracle()`.

---

### Recommendation

Add a zero-rate guard in `viewSwapRsETHAmountAndFee()`:

```solidity
require(rsETHToETHrate > 0, "Rate not initialised");
```

Alternatively, add a minimum-rate check inside `CrossChainRateReceiver.lzReceive()` to reject a zero payload, and revert in `getRate()` if `rate == 0`.

---

### Proof of Concept

```solidity
// Local fork test (no mainnet)
function testDepositRevertsWhenRateIsZero() public {
    // Deploy receiver — rate defaults to 0
    RSETHRateReceiver receiver = new RSETHRateReceiver(
        srcChainId, address(provider), address(lzEndpoint)
    );

    // Deploy pool pointing at the receiver as oracle
    RSETHPoolV2NBA pool = new RSETHPoolV2NBA();
    pool.initialize(admin, bridger, address(wrsETH), 10, address(receiver));

    // rate == 0 → deposit must revert
    vm.expectRevert(); // Panic: division by zero
    pool.deposit{value: 1 ether}("ref");

    // Deliver a valid rate via lzReceive
    bytes memory payload = abi.encode(uint256(1.05e18));
    vm.prank(address(lzEndpoint));
    receiver.lzReceive(srcChainId, abi.encodePacked(address(provider)), 0, payload);

    // Now deposit succeeds
    pool.deposit{value: 1 ether}("ref"); // no revert
}
```

### Citations

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L13-13)
```text
    uint256 public rate;
```

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L95-95)
```text
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
