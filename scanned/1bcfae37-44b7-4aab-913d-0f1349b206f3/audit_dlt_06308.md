# [M] Weights are not updated on each _update action but only when nearing the target time, due to precision loss

## Summary
Severity: Medium
Chain: Smart contract
Component: Catalyst-Exchange
Published: 2024-02-03
Source: https://github.com/hats-finance/Catalyst-Exchange-0x3026c1ea29bf1280f99b41934b2cb65d053c9db4/issues/78
Type: hats-finding

## Details
**Github username:** @nuthan2x
**Twitter username:** nuthan2x
**Submission hash (on-chain):** 0x75401aa9cc642d6ae1209ca04b56d7e3b72e29d10e255d616f92bcccd2d19f77
**Severity:** medium

**Description:**
**Description**\
The weights of the vaults can be updated by vault deployer due to market conditions and adaptability. And the weights are updated on each transaction of swap/liquidity actions, and they will be linearly updated until the target time is reached. But some weights changes are not updated during the first 85% of the time but only starts to update on the rest 15%. This is due to the presion loss mentioned in the below sections.

**Attack Scenario**\
- Code from [CatalystVaultVolatile::_updateWeights](https://github.com/hats-finance/Catalyst-Exchange-0x3026c1ea29bf1280f99b41934b2cb65d053c9db4/blob/27b4d0a2bca177aff00def8cd745623bfbf7cb6b/evm/src/CatalystVaultVolatile.sol#L240-L242)

```solidity
    if (targetWeight > currentWeight) {
        // if the weights are increased then targetWeight - currentWeight > 0.
        // Add the change to the current weight.
        uint256 newWeight = currentWeight + (
@--->        (targetWeight - currentWeight) * (block.timestamp - lastModification)
@--->   ) / (adjTarget - lastModification);
        _weight[token] = newWeight;
        wsum += newWeight;
    } else {
        // if the weights are decreased then targetWeight - currentWeight < 0.
        // Subtract the change from the current weights.
        uint256 newWeight = currentWeight - (
            (currentWeight - targetWeight) * (block.timestamp - lastModification)
        ) / (adjTarget - lastModification);
        _weight[token] = newWeight;
        wsum += newWeight;
    }
```

- The issue is due to the huge denominator in the above code at `(adjTarget - lastModification)` ex: (14 days - 1 hours), but numerator will be `(targetWeight - currentWeight) * (block.timestamp - lastModification)` ex: (20 - 10) * (1 hours) which is a precision loss.

Exact flow of issue:

1. create a vault with (50% per each asset weight) at [10,10] being the weights.
2. Now due to market conditions, the vault deployer changes the weights to (66% - 33%) in [20,10] as the weights for 14 days adjustment period.
3. Now the weights have to be increased for asset A, and asset B remains same. And the increase asset A's weight should be linear and to be updated on every action. 
4. but since the the difference in numbers (20 - 10) == 10  is very low and using time as denominator in the below code makes the precision loss. 
5. So weights are updated from 10 to 11, 11 to 12 on the last 2 days transactions, but for last 12 days the weights remains same and not updated. Atleast the weights should have been linearly updated like (10 weights/14 days) like 0.7 per day time based.

**Attachments**

1. **Proof of Concept (PoC) File**

- The weights are updated from 10 to 20 for asset A, and for 14 days. It is assumed someone calls update function once evry 4 hours average.
- See the logs, the weights are updated linearly only on the last 2 days (40 hours) of the loop.
- Check the POC on this [gist](https://gist.github.com/nuthan2x/b5c6eb8ac801ddab4d2d6593dad7c6e5)

```sh
Running 1 test for test/Test2POC.sol:Testing
[PASS] testWeightsUpdate() (gas: 13887541)
Logs:
  after 0 hours
  DAI weight before update:  10
  DAI weight afrter update:  10

  after 4 hours
  DAI weight before update:  10
  DAI weight afrter update:  10

  after 8 hours
  DAI weight before update:  10
  DAI weight afrter update:  10

  after 12 hours
  DAI weight before update:  10
  DAI weight afrter update:  10

  after 16 hours
  DAI weight before update:  10
  DAI weight afrter update:  10

  after 20 hours
  DAI weight before update:  10
  DAI weight afrter update:  10

  after 24 hours
  DAI weight before update:  10
  DAI weight afrter update:  10

  ///////////////////////// logs removed  for simplicity ///////////////////////

  after 276 hours
  DAI weight before update:  10
  DAI weight afrter update:  10

  after 280 hours
  DAI weight before update:  10
  DAI weight afrter update:  10

  after 284 hours
  DAI weight before update:  10
  DAI weight afrter update:  10

  after 288 hours
  DAI weight before update:  10
  DAI weight afrter update:  10

  after 292 hours
  DAI weight before update:  10
  DAI weight afrter update:  10

  after 296 hours
  DAI weight before update:  10
  DAI weight afrter update:  11

  after 300 hours
  DAI weight before update:  11
  DAI weight afrter update:  12

  after 304 hours
  DAI weight before update:  12
  DAI weight afrter update:  13

  after 308 hours
  DAI weight before update:  13
  DAI weight afrter update:  14

  after 312 hours
  DAI weight before update:  14
  DAI weight afrter update:  15

  after 316 hours
  DAI weight before update:  15
  DAI weight afrter update:  16

  after 320 hours
  DAI weight before update:  16
  DAI weight afrter update:  17

  after 324 hours
  DAI weight before update:  17
  DAI weight afrter update:  18

  after 328 hours
  DAI weight before update:  18
  DAI weight afrter update:  19

  after 332 hours
  DAI weight before update:  19
  DAI weight afrter update:  20


Test result: ok. 1 passed; 0 failed; 0 skipped; finished in 86.58ms
```


2. **Revised Code File (Optional)**

- The fix is either change the calculation or add precision. Adding precision is easy by setting the standard, that weights should be in denomiantion of base points (10_000). Now due to this increase, the max unit capacity also increases due to its dependence on `wsum`

- Now run the same POC with w1 = 10_000, w2 = 10_000 initially, and target weights as [20_000, 10_000], the weights are updated with correct precision linearly. Check the same weight model change with precision.

```sh
[PASS] testWeightsUpdate() (gas: 13990786)
Logs:
  after 0 hours
  DAI weight before update:  10000
  DAI weight afrter update:  10119

  after 4 hours
  DAI weight before update:  10119
  DAI weight afrter update:  10238

  after 8 hours
  DAI weight before update:  10238
  DAI weight afrter update:  10357

  after 12 hours
  DAI weight before update:  10357
  DAI weight afrter update:  10476

  after 16 hours
  DAI weight before update:  10476
  DAI weight afrter update:  10595

  after 20 hours
  DAI weight before update:  10595
  DAI weight afrter update:  10714

  after 24 hours
  DAI weight before update:  10714
  DAI weight afrter update:  10833

  after 28 hours
  DAI weight before update:  10833
  DAI weight afrter update:  10952

  after 32 hours
  DAI weight before update:  10952
  DAI weight afrter update:  11071

  after 36 hours
  DAI weight before update:  11071
  DAI weight afrter update:  11190

  after 40 hours
  DAI weight before update:  11190
  DAI weight afrter update:  11309

  after 44 hours
  DAI weight before update:  11309
  DAI weight afrter update:  11428

  after 48 hours
  DAI weight before update:  11428
  DAI weight afrter update:  11547

  after 52 hours
  DAI weight before update:  11547
  DAI weight afrter update:  11666

  after 56 hours
  DAI weight before update:  11666
  DAI weight afrter update:  11785

  after 60 hours
  DAI weight before update:  11785
  DAI weight afrter update:  11904


  ///////////////////////// logs removed  for simplicity ///////////////////////

  

  after 296 hours
  DAI weight before update:  18806
  DAI weight afrter update:  18925

  after 300 hours
  DAI weight before update:  18925
  DAI weight afrter update:  19044

  after 304 hours
  DAI weight before update:  19044
  DAI weight afrter update:  19163

  after 308 hours
  DAI weight before update:  19163
  DAI weight afrter update:  19282

  after 312 hours
  DAI weight before update:  19282
  DAI weight afrter update:  19401

  after 316 hours
  DAI weight before update:  19401
  DAI weight afrter update:  19520

  after 320 hours
  DAI weight before update:  19520
  DAI weight afrter update:  19640

  after 324 hours
  DAI weight before update:  19640
  DAI weight afrter update:  19760

  after 328 hours
  DAI weight before update:  19760
  DAI weight afrter update:  19880

  after 332 hours
  DAI weight before update:  19880
  DAI weight afrter update:  20000


Test result: ok. 1 passed; 0 failed; 0 skipped; finished in 81.81ms
```
