### Title
Unbounded Gas in `getETHDistributionData()` via Unbounded `getQueuedWithdrawals` Iteration in `getAssetUnstaking` — (`contracts/NodeDelegator.sol`)

---

### Summary

`updateRSETHPrice()` is publicly callable and has no gas cap. Its call chain reaches `getETHDistributionData()`, which calls `getAssetUnstaking(ETH_TOKEN)` on every NDC. Each such call fetches the full `getQueuedWithdrawals` array from EigenLayer's `DelegationManager` and iterates it in Solidity with no bound. With enough queued beacon-chain withdrawals across NDCs, the transaction exhausts block gas and `updateRSETHPrice()` becomes permanently uncallable.

---

### Finding Description

**Full call chain:**

```
updateRSETHPrice()                          [public, whenNotPaused only]
  └─ _updateRsETHPrice()
       └─ _getTotalEthInProtocol()
            └─ getTotalAssetDeposits(ETH_TOKEN)
                 └─ getAssetDistributionData(ETH_TOKEN)
                      └─ getETHDistributionData()
                           └─ for each NDC:
                                getAssetUnstaking(ETH_TOKEN)
                                  └─ DelegationManager.getQueuedWithdrawals(ndc)
                                       → iterate ALL returned Withdrawal[] structs
```

**`getETHDistributionData()` in `LRTDepositPool.sol`:** [1](#0-0) 

For every NDC in `nodeDelegatorQueue`, it calls `getAssetUnstaking(LRTConstants.ETH_TOKEN)`.

**`getAssetUnstaking()` in `NodeDelegator.sol`:** [2](#0-1) 

This function:
1. Makes an external call to `DelegationManager.getQueuedWithdrawals(address(this))`, which returns the **entire** `Withdrawal[]` array for that NDC — unbounded in size.
2. ABI-decodes the full array into memory (expensive for large arrays).
3. Iterates every `Withdrawal` struct and every `strategies[]` entry within it.

There is no cap on the number of queued withdrawals per NDC in EigenLayer. Each beacon-chain validator withdrawal is a separate `queueWithdrawals` call, so a protocol with many validators per NDC will naturally accumulate a large queue.

**`updateRSETHPrice()` has no access control beyond `whenNotPaused`:** [3](#0-2) 

Anyone can call it, and it must complete within a single block's gas budget.

**`_getTotalEthInProtocol()` iterates all supported assets, calling `getTotalAssetDeposits` for each:** [4](#0-3) 

When `ETH_TOKEN` is a supported asset, this triggers the full ETH distribution path.

**Gas complexity:** `O(NDCs × queued_withdrawals_per_NDC × strategies_per_withdrawal)`. With `maxNodeDelegatorLimit = 10` NDCs and, say, 80 queued withdrawals per NDC (each a separate beacon-chain validator exit), that is 800+ Solidity loop iterations plus 10 large ABI-decode operations from EigenLayer. The memory allocation and decoding of large `Withdrawal[]` arrays alone can push the transaction past the 30M block gas limit. [5](#0-4) 

---

### Impact Explanation

When the gas cost of `updateRSETHPrice()` exceeds the block gas limit:

- The rsETH price (`rsETHPrice`) can no longer be updated.
- Protocol fee accrual (rsETH minted to treasury) stops permanently.
- `updateRSETHPriceAsManager()` is also affected since it calls the same `_updateRsETHPrice()` internal function. [6](#0-5) 

This matches **Medium — Unbounded gas consumption**, with secondary impact of **Medium — Permanent freezing of unclaimed yield** (protocol fees can never be minted again).

---

### Likelihood Explanation

- The protocol operates beacon-chain validators. Each validator exit queues a separate withdrawal in EigenLayer. A protocol with 80+ active validator exits per NDC is operationally realistic at scale.
- The condition is reached through entirely normal protocol operation — no attacker action is required. The state accumulates organically.
- `updateRSETHPrice()` is public, so any caller (including automated keepers) will hit the OOG revert once the threshold is crossed.
- There is no administrative escape hatch: even `updateRSETHPriceAsManager()` calls the same unbounded path.

---

### Recommendation

1. **Paginate or snapshot queued withdrawals off-chain.** Instead of computing `getAssetUnstaking` on-chain by iterating EigenLayer's full queue, maintain an on-chain accounting variable that is incremented when a withdrawal is queued and decremented when it is completed.

2. **Alternatively**, add a hard cap on the number of queued withdrawals iterated per NDC per call, and revert or skip if the cap is exceeded, so the function degrades gracefully rather than OOG-reverting.

3. **Decouple price update from full TVL recomputation.** Allow partial TVL updates or cache intermediate results to avoid recomputing the entire state in a single transaction.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// Fork test (local fork, no public mainnet)
// Setup: deploy mock EigenLayer DelegationManager that returns 80 Withdrawal structs
// for each of 10 NDCs when getQueuedWithdrawals() is called.
// Each Withdrawal has 1 strategy = beaconChainETHStrategy.

contract MockDelegationManager {
    function getQueuedWithdrawals(address)
        external
        view
        returns (IDelegationManager.Withdrawal[] memory withdrawals, uint256[][] memory shares)
    {
        withdrawals = new IDelegationManager.Withdrawal[](80);
        shares = new uint256[][](80);
        for (uint256 i = 0; i < 80; i++) {
            withdrawals[i].strategies = new IStrategy[](1);
            withdrawals[i].strategies[0] = IStrategy(BEACON_CHAIN_ETH_STRATEGY);
            withdrawals[i].scaledShares = new uint256[](1);
            withdrawals[i].scaledShares[0] = 32 ether;
            shares[i] = new uint256[](1);
            shares[i][0] = 32 ether;
        }
    }
}

// In the test:
// 1. Wire 10 NDCs, each backed by MockDelegationManager above.
// 2. Call updateRSETHPrice() and measure gas.
// 3. Assert gas < 30_000_000 (block limit).
// Expected: assertion FAILS — gas exceeds block limit due to
//   10 NDCs × 80 withdrawals × ABI-decode + iteration cost.
```

### Citations

**File:** contracts/LRTDepositPool.sol (L29-33)
```text
    uint256 public maxNodeDelegatorLimit;
    uint256 public minAmountToDeposit;

    mapping(address => uint256) public isNodeDelegator; // 0: not a node delegator, 1: is a node delegator
    address[] public nodeDelegatorQueue;
```

**File:** contracts/LRTDepositPool.sol (L484-493)
```text
        for (uint256 i; i < ndcsCount;) {
            ethLyingInNDCs += nodeDelegatorQueue[i].balance;

            ethStakedInEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getEffectivePodShares();
            ethUnstakingFromEigenLayer += INodeDelegator(nodeDelegatorQueue[i])
                .getAssetUnstaking(LRTConstants.ETH_TOKEN);
            unchecked {
                ++i;
            }
        }
```

**File:** contracts/NodeDelegator.sol (L405-427)
```text
    function getAssetUnstaking(address asset) external view returns (uint256 amount) {
        (IDelegationManager.Withdrawal[] memory queuedWithdrawals, uint256[][] memory withdrawalShares) =
            _getDelegationManager().getQueuedWithdrawals(address(this));

        for (uint256 withdrawalIndex = 0; withdrawalIndex < queuedWithdrawals.length; withdrawalIndex++) {
            IDelegationManager.Withdrawal memory withdrawal = queuedWithdrawals[withdrawalIndex];

            for (uint256 strategyIndex = 0; strategyIndex < withdrawal.strategies.length; strategyIndex++) {
                IStrategy strategy = withdrawal.strategies[strategyIndex];

                address strategyAsset = address(strategy) == address(lrtConfig.beaconChainETHStrategy())
                    ? LRTConstants.ETH_TOKEN
                    : address(strategy.underlyingToken());

                if (strategyAsset != asset) continue;

                uint256 sharesToUnstake = withdrawalShares[withdrawalIndex][strategyIndex];
                amount += strategyAsset == LRTConstants.ETH_TOKEN
                    ? sharesToUnstake
                    : strategy.sharesToUnderlyingView(sharesToUnstake);
            }
        }
    }
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L94-96)
```text
    function updateRSETHPriceAsManager() external onlyLRTManager {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L331-349)
```text
    function _getTotalEthInProtocol() private view returns (uint256 totalETHInProtocol) {
        address lrtDepositPoolAddr = lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL);
        address[] memory supportedAssets = lrtConfig.getSupportedAssetList();
        uint256 supportedAssetCount = supportedAssets.length;

        for (uint16 assetIdx; assetIdx < supportedAssetCount;) {
            address asset = supportedAssets[assetIdx];
            // assetER is in 1e18 precision (1.0 = 1e18)
            uint256 assetER = getAssetPrice(asset);
            // totalAssetAmt is in 1e18 precision (standard token decimals)
            uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

            totalETHInProtocol += totalAssetAmt.mulWad(assetER);

            unchecked {
                ++assetIdx;
            }
        }
    }
```
