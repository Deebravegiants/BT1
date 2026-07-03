### Title
Protocol Treasury Fee Bypass via Unrestricted `sendFunds()` in `FeeReceiver` - (File: contracts/FeeReceiver.sol)

### Summary

The `FeeReceiver` contract is initialized with a mandatory non-zero `_protocolFeePercentInBPS` (the treasury's share of MEV/execution-layer rewards), but the only fund-distribution function, `sendFunds()`, forwards 100% of the contract's ETH balance directly to the deposit pool without deducting any treasury fee. Because `sendFunds()` has no access control, any external caller can trigger it at any time, permanently bypassing the treasury fee split and routing all MEV rewards to rsETH holders instead.

### Finding Description

`FeeReceiver.initialize()` enforces that `_protocolFeePercentInBPS != 0` and stores it in `_legacyProtocolFeePercentInBPS`, alongside the treasury address in `_legacyProtocolTreasury`. This makes the fee split a required protocol invariant at deployment time. [1](#0-0) 

However, `sendFunds()` — the only mechanism to distribute accumulated ETH — sends the entire balance to the deposit pool with no fee deduction: [2](#0-1) 

`_legacyProtocolTreasury` and `_legacyProtocolFeePercentInBPS` are never read anywhere in the contract's execution logic. The function carries no `onlyRole` or similar modifier, making it callable by any EOA or contract.

### Impact Explanation

Every time MEV or execution-layer rewards accumulate in `FeeReceiver`, the treasury's entitled share (up to the configured BPS) is silently forfeited. All rewards are instead credited to `LRTDepositPool` via `receiveFromRewardReceiver()`, inflating the rsETH exchange rate for all holders. The treasury — the intended fee recipient — receives nothing. This constitutes ongoing theft of unclaimed yield from the protocol treasury.

**Impact: High** — Theft of unclaimed yield (treasury's share of MEV rewards).

### Likelihood Explanation

`sendFunds()` is a public, permissionless function. Any actor (including a competing protocol, a griefing bot, or an rsETH holder who benefits from the inflated rate) can call it at any time. No special privilege, capital, or timing is required. The call is cheap and repeatable, making sustained exploitation trivial.

**Likelihood: High.**

### Recommendation

1. Implement the fee split inside `sendFunds()`: compute `fee = balance * _legacyProtocolFeePercentInBPS / 10_000`, transfer `fee` to `_legacyProtocolTreasury`, and forward only the remainder to the deposit pool.
2. Add an access-control modifier (e.g., `onlyRole(LRTConstants.MANAGER)`) to `sendFunds()` so that only authorized operators can trigger distribution, preventing griefing or front-running of fee collection.

### Proof of Concept

1. MEV rewards accumulate in `FeeReceiver` (e.g., 10 ETH, with `_legacyProtocolFeePercentInBPS = 1000` → treasury should receive 1 ETH).
2. Any external address calls `FeeReceiver.sendFunds()`.
3. `sendFunds()` calls `ILRTDepositPool(depositPool).receiveFromRewardReceiver{value: 10 ETH}()` — forwarding the full 10 ETH.
4. `_legacyProtocolTreasury` receives 0 ETH instead of the entitled 1 ETH.
5. rsETH holders gain the full 10 ETH in backing value; the treasury is permanently deprived of its fee. [2](#0-1) [3](#0-2)

### Citations

**File:** contracts/FeeReceiver.sol (L23-47)
```text
    function initialize(
        address _protocolTreasury,
        address _depositPool,
        uint256 _protocolFeePercentInBPS,
        address admin,
        address manager
    )
        external
        initializer
    {
        if (
            _protocolTreasury == address(0) || _depositPool == address(0) || _protocolFeePercentInBPS == 0
                || admin == address(0) || manager == address(0)
        ) {
            revert InvalidEmptyValue();
        }

        _legacyProtocolTreasury = _protocolTreasury;
        depositPool = _depositPool;
        _legacyProtocolFeePercentInBPS = _protocolFeePercentInBPS;

        __AccessControl_init();
        _setupRole(DEFAULT_ADMIN_ROLE, admin);
        _setupRole(LRTConstants.MANAGER, manager);
    }
```

**File:** contracts/FeeReceiver.sol (L53-58)
```text
    function sendFunds() external {
        uint256 balance = address(this).balance;
        ILRTDepositPool(depositPool).receiveFromRewardReceiver{ value: balance }();

        emit MevRewardsAddedToTVL(balance);
    }
```
