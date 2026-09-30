# [M] `StabilizerNode.stabilize

## Summary
Severity: Medium
Contest weight: 0.5764
Dataset id: 18139
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The contract contains a logical accounting flaw in the way it records the time of the last pool tracking operation. The function that is supposed to keep the pool state consistent, stabilize(), invokes the external data lab to track the pool but fails to update the internal timestamp variable lastTracking. The separate function trackPool() also tracks the pool and, as part of its incentive mechanism, checks that a configurable interval (trackingBackoff) has elapsed since the last tracking event before allowing a caller to receive a small mint reward. Because stabilize() does not refresh lastTracking, an attacker can call stabilize() and then immediately call trackPool() without waiting for the required back‑off period. The contract will consider the call valid, execute the external tracking, and mint incentive tokens to the caller. This results in unnecessary token inflation, reducing the value of existing holders and potentially draining the protocol’s token reserves over time. The issue appears only when both functions are used in succession; normal operation that relies solely on trackPool() after the back‑off period would not expose the bug, making it easy to overlook in routine testing. The problem was identified during a manual audit that compared state updates across related functions and noticed that the timestamp was only set in trackPool(). To remediate, the stabilize() implementation should assign lastTracking = block.timestamp after successfully invoking the data lab, mirroring the behaviour of trackPool(). This change restores the intended accounting invariant that only one incentive can be earned per trackingBackoff interval, preventing the extra minting and preserving the protocol’s economic model.

## Proof of Concept
`trackPool()` pays an incentive per `trackingBackoff` in order to ensure pool consistency.

```solidity
File: 2023-02-malt\contracts\StabilityPod\StabilizerNode.sol
248:   function trackPool() external onlyActive {
249:     require(block.timestamp >= lastTracking + trackingBackoff, "Too early"); // @audit lastTracking should be updated in stabilize() also
250:     bool success = maltDataLab.trackPool();
251:     require(success, "Too early");
252:     malt.mint(msg.sender, (trackingIncentive * (10**malt.decimals())) / 100); // div 100 because units are cents
253:     lastTracking = block.timestamp;
254:     emit Tracking();
255:   }
```

And `stabilize()` tracks the pool as well and we don’t need to pay an incentive unnecessarily in `trackPool()` if `stabilize()` was called recently.

For that, we can update `lastTracking` in `stabilize()`.

## Recommendation
Recommend updating `lastTracking` in `stabilize()`.

```solidity
function stabilize() external nonReentrant onlyEOA onlyActive whenNotPaused {
  // Ensure data consistency
  maltDataLab.trackPool();
  lastTracking = block.timestamp; //++++++++++++++++

  ...
```
