# [M] Potential Congestion due to lack of `batchingInterval` and `maxTransfersPerBatch` modification Function in `OutgoingQueue` Contract

## Summary
Severity: Medium
Chain: Smart contract
Component: illuminex
Published: 2024-07-03
Source: https://github.com/hats-finance/illuminex-0x0bb4aa1f58719707405c231fcdf0b405714799cf/issues/18
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0x8a69d8b09705e81418e7d4380381651976193b755987c6af7553e5381b6bf96c
**Severity:** medium

**Description:**
**Description:**

`OutgoingQueue` contract defines a batching mechanism for outgoing transfers with a fixed `batchingInterval` of 15 minutes. This interval determines how frequently batches of transfers can be processed. However, the contract does not provide a function to modify the `batchingInterval`, potentially leading to issues if the interval needs to be adjusted in response to changing conditions or requirements.

In addition, maximum transfer per batch is 5, and again, there is no way to increase this value.

With a simple calculation, given that `maxTransfersPerBatch` is 5 and `batchingInterval` is 15 minutes, we can determine how many batches can be processed in a day.

> There are 24 hours in a day, each hour has 60 minutes, 1440 minutes in a day.

> Given that each batching interval is 15 minutes, 1440/15 = 96 batches per day

> If each batch can handle a maximum of 5 transfers, then the total number of transfers per day is  96 x 5 = 480 transfers per day.

Therefore, given that `maxTransfersPerBatch` is 5 and `batchingInterval` is 15 minutes, the contract can handle up to 480 transfers per day.

When the transfer exceed this number, it will increase waiting duration, and bottleneck will occur.

**Impact:**

As the usage of the contract grows, the fixed batching interval may become a bottleneck. If the volume of outgoing transfers increases significantly, a fixed interval of 15 minutes might not be sufficient to process all transfers in a timely manner. This could lead to congestion and delays in processing transfers.

**Mitigation:**
Consider to implement a function to modify the `batchingInterval` and `maxTransfersPerBatch`, and function should only be callable by an authorized address.
