No vulnerability found for this question.

The report's bug class is unbounded storage-array traversal (`depositsQueued`/`withdrawsQueued` looping over ever-growing `deposits`/`withdraws` arrays) causing gas-cost DoS. Searching alt.fun's in-scope contracts for an analogous pattern:

- `Bonding.sol` contains only one loop, and it is bounded to exactly 3 iterations over `params.urls` in `launch()` — not user-growable. [1](#0-0) 
- `FeeVault.sol` explicitly avoids this exact bug class: fee accounting uses O(1) running accumulators (`totalAccruedCreator`, `protocolBalance`) rather than iterating a growing array/mapping, and its own docstring states this was a deliberate design choice ("Lets `accrue` do its underfund check in O(1) without iterating the creator mapping"). [2](#0-1) [3](#0-2) 
- `FeeVault.getDepositors()` and `Bonding.getRouters()` do return full `EnumerableSet` arrays via `.values()`, but these sets are only mutated by `onlyOwner` (`addDepositor`/`removeDepositor`, `addRouter`/`removeRouter`), so no unprivileged trader/creator/wallet can grow them to a DoS-inducing size. [4](#0-3) [5](#0-4) 

No other in-scope contract (`Zap.sol`, `Router.sol`, `Pair.sol`, `LPLock.sol`, `Token.sol`) stores a per-user-appendable array that is summed/iterated in a state-changing or fund-critical path reachable by `Zap.createToken/buy/sell`, `Bonding.triggerGraduation/finalizeGraduation/transferCreator`, or `FeeVault.claim/claimProtocol/sweepDonations`. The DoS-via-unbounded-array-sum bug class from the Sherlock report has no reachable analog in alt.fun's actual contract shape.

### Citations

**File:** packages/contracts/src/Bonding.sol (L408-410)
```text
        for (uint256 i = 0; i < 3; i++) {
            if (bytes(params.urls[i]).length > MAX_URL_LENGTH) revert InvalidUrlLength();
        }
```

**File:** packages/contracts/src/Bonding.sol (L850-875)
```text
    function addRouter(
        address router_
    ) external onlyOwner {
        if (router_ == address(0)) revert ZeroAddress();
        if (!_s().routers.add(router_)) revert RouterAlreadyAdded();
        emit RouterAdded(router_);
    }

    function removeRouter(
        address router_
    ) external onlyOwner {
        EnumerableSet.AddressSet storage routers_ = _s().routers;
        if (!routers_.remove(router_)) revert RouterNotFound();
        if (routers_.length() == 0) revert MustKeepOneRouter();
        emit RouterRemoved(router_);
    }

    function isRouter(
        address router_
    ) external view returns (bool) {
        return _s().routers.contains(router_);
    }

    function getRouters() external view returns (address[] memory) {
        return _s().routers.values();
    }
```

**File:** packages/contracts/src/FeeVault.sol (L41-44)
```text
        /// @notice Running sum of unclaimed creator balances. Lets `accrue`
        ///         do its underfund check in O(1) without iterating the
        ///         creator mapping.
        uint256 totalAccruedCreator;
```

**File:** packages/contracts/src/FeeVault.sol (L101-123)
```text
    function accrue(
        address token,
        address creator,
        uint256 creatorAmount,
        uint256 protocolAmount,
        bool isBuy
    ) external onlyDepositor {
        FeeVaultStorage storage $ = _s();
        if (creatorAmount > 0) {
            if (creator == address(0)) revert ZeroAddress();
            $.creatorBalance[creator] += creatorAmount;
            $.totalAccruedCreator += creatorAmount;
            $.lifetimeCreatorEarned[creator] += creatorAmount;
        }
        if (protocolAmount > 0) {
            $.protocolBalance += protocolAmount;
            $.lifetimeProtocolEarned += protocolAmount;
        }
        if ($.usdc.balanceOf(address(this)) < $.totalAccruedCreator + $.protocolBalance) {
            revert UnderfundedAccrual();
        }
        emit FeeAccrued(token, creator, creatorAmount, protocolAmount, isBuy);
    }
```

**File:** packages/contracts/src/FeeVault.sol (L164-177)
```text
    function addDepositor(
        address depositor
    ) external onlyOwner {
        if (depositor == address(0)) revert ZeroAddress();
        if (!_s().depositors.add(depositor)) revert DepositorAlreadyAdded();
        emit DepositorAdded(depositor);
    }

    function removeDepositor(
        address depositor
    ) external onlyOwner {
        if (!_s().depositors.remove(depositor)) revert DepositorNotFound();
        emit DepositorRemoved(depositor);
    }
```
