### Title
Daily Mint Limit Can Be Exhausted by Any Depositor to DoS L2 Pool Deposits for Up to 24 Hours - (File: contracts/pools/RSETHPoolV2.sol, contracts/pools/RSETHPoolV3.sol, contracts/pools/RSETHPoolV3ExternalBridge.sol, contracts/pools/RSETHPoolV3WithNativeChainBridge.sol)

---

### Summary

The L2 pool contracts enforce a `dailyMintLimit` on wrsETH minting. Because the `deposit()` function is publicly callable with no minimum cost when `feeBps = 0` (or negligible cost when `feeBps` is small), any unprivileged user can exhaust the entire daily mint quota in a single transaction. Once exhausted, all subsequent `deposit()` calls revert with `DailyMintLimitExceeded` for up to 24 hours. The attacker retains the wrsETH they received, making the net cost of the attack only the deposit fee and L2 gas.

---

### Finding Description

All four L2 pool contracts share the same `limitDailyMint` modifier pattern. In `RSETHPoolV2.sol`:

```solidity
modifier limitDailyMint(uint256 amount) {
    ...
    (uint256 rsETHAmount,) = viewSwapRsETHAmountAndFee(amount);
    uint256 currentDay = getCurrentDay();
    if (currentDay > lastMintDay) {
        lastMintDay = currentDay;
        dailyMintAmount = 0;
    }
    if (dailyMintAmount + rsETHAmount > dailyMintLimit) {
        revert DailyMintLimitExceeded();
    }
    dailyMintAmount += rsETHAmount;
    _;
}
``` [1](#0-0) 

The `deposit()` function is publicly accessible and applies this modifier:

```solidity
function deposit(string memory referralId) external payable nonReentrant whenNotPaused limitDailyMint(msg.value) {
``` [2](#0-1) 

The fee charged on deposit is:

```solidity
fee = amount * feeBps / 10_000;
``` [3](#0-2) 

`feeBps` is set at initialization with no lower-bound validation, meaning it can be zero: [4](#0-3) 

The identical `limitDailyMint` pattern and publicly callable `deposit()` exist in `RSETHPoolV3.sol`, `RSETHPoolV3ExternalBridge.sol`, and `RSETHPoolV3WithNativeChainBridge.sol`: [5](#0-4) [6](#0-5) [7](#0-6) 

There is no reverse-swap path available to regular users — `swapAssetToPremintedRsETH` is restricted to `OPERATOR_ROLE` — so the attacker simply holds wrsETH after the attack: [8](#0-7) 

---

### Impact Explanation

Once `dailyMintAmount` reaches `dailyMintLimit`, every subsequent `deposit()` call from any user reverts with `DailyMintLimitExceeded` until the next 24-hour window resets the counter. This is a **temporary freezing of the deposit functionality** for all L2 pool users for up to 24 hours per attack cycle. The attack can be repeated every day at the cost of only the deposit fee (zero if `feeBps = 0`) plus cheap L2 gas, while the attacker retains the full value of the wrsETH received.

**Impact: Medium — Temporary freezing of funds (deposit access).**

---

### Likelihood Explanation

- The `deposit()` entry point is fully public with no access control.
- L2 gas costs are negligible (Arbitrum, Optimism, Base, etc.).
- If `feeBps = 0`, the attack is economically free; even with a non-zero fee the attacker holds liquid wrsETH they can sell on a DEX, recovering most of the capital.
- The attack requires a single transaction per day and no special privileges.
- The daily limit is a known, queryable on-chain value (`dailyMintLimit`), making it trivial to size the attack deposit precisely.

**Likelihood: Medium.**

---

### Recommendation

1. **Enforce a non-zero minimum fee**: Add a `require(_feeBps > 0)` check in `initialize()` and in any `setFeeBps` setter so that every deposit carries a real economic cost that is permanently lost (not recoverable via wrsETH sale).
2. **Per-address sub-limits**: Introduce a per-address daily deposit cap so no single address can consume the entire global quota.
3. **Cooldown between deposits**: Require a minimum time gap between successive deposits from the same address.

---

### Proof of Concept

Assume `dailyMintLimit = 1000 wrsETH`, `feeBps = 0`, and the current rsETH/ETH rate is 1.05.

1. Attacker computes the ETH needed: `ethNeeded = 1000 * 1.05 = 1050 ETH` (or the exact amount to mint exactly `dailyMintLimit` wrsETH).
2. Attacker calls `RSETHPoolV2.deposit{value: 1050 ether}("")`.
3. Inside `limitDailyMint`: `rsETHAmount = 1000`, `dailyMintAmount + 1000 == dailyMintLimit` → passes; `dailyMintAmount` is set to `1000`.
4. Attacker receives 1000 wrsETH. Fee paid = 0 (feeBps = 0). Net cost = L2 gas only.
5. Any subsequent call to `deposit()` by any user reverts: `dailyMintAmount + any_amount > dailyMintLimit`.
6. All L2 pool deposits are blocked for up to 24 hours.
7. Attacker repeats the next day. [1](#0-0) [9](#0-8)

### Citations

**File:** contracts/pools/RSETHPoolV2.sol (L72-94)
```text
    modifier limitDailyMint(uint256 amount) {
        if (block.timestamp < startTimestamp) {
            revert MintBeforeStartTimestamp();
        }

        // Calculate the amount of rsETH that will be minted
        (uint256 rsETHAmount,) = viewSwapRsETHAmountAndFee(amount);
        uint256 currentDay = getCurrentDay();

        // If the current day is greater than the last mint day, reset the daily mint amount
        if (currentDay > lastMintDay) {
            lastMintDay = currentDay;
            dailyMintAmount = 0;
        }

        // Check if the daily mint amount plus the amount to mint is greater than the daily mint limit
        if (dailyMintAmount + rsETHAmount > dailyMintLimit) {
            revert DailyMintLimitExceeded();
        }

        dailyMintAmount += rsETHAmount;
        _;
    }
```

**File:** contracts/pools/RSETHPoolV2.sol (L176-198)
```text
    function initialize(
        address admin,
        address bridger,
        address _wrsETH,
        uint256 _feeBps,
        address _rsETHOracle
    )
        external
        initializer
    {
        UtilLib.checkNonZeroAddress(_wrsETH);
        UtilLib.checkNonZeroAddress(_rsETHOracle);
        __ERC20_init("rsETH", "rsETH");
        __AccessControl_init();
        __ReentrancyGuard_init();
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _setupRole(BRIDGER_ROLE, admin);
        _setupRole(BRIDGER_ROLE, bridger);

        wrsETH = IERC20WrsETH(_wrsETH);
        feeBps = _feeBps;
        rsETHOracle = _rsETHOracle;
    }
```

**File:** contracts/pools/RSETHPoolV2.sol (L207-219)
```text
    function deposit(string memory referralId) external payable nonReentrant whenNotPaused limitDailyMint(msg.value) {
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
    }
```

**File:** contracts/pools/RSETHPoolV2.sol (L226-226)
```text
        fee = amount * feeBps / 10_000;
```

**File:** contracts/pools/RSETHPoolV3.sol (L96-125)
```text
    modifier limitDailyMint(uint256 amount, address token) {
        if (block.timestamp < startTimestamp) {
            revert MintBeforeStartTimestamp();
        }

        uint256 rsETHAmount;

        // Calculate the amount of rsETH that will be minted
        if (token == ETH_IDENTIFIER) {
            (rsETHAmount,) = viewSwapRsETHAmountAndFee(amount);
        } else {
            (rsETHAmount,) = viewSwapRsETHAmountAndFee(amount, token);
        }

        uint256 currentDay = getCurrentDay();

        // If the current day is greater than the last mint day, reset the daily mint amount
        if (currentDay > lastMintDay) {
            lastMintDay = currentDay;
            dailyMintAmount = 0;
        }

        // Check if the daily mint amount plus the amount to mint is greater than the daily mint limit
        if (dailyMintAmount + rsETHAmount > dailyMintLimit) {
            revert DailyMintLimitExceeded();
        }

        dailyMintAmount += rsETHAmount;
        _;
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L414-423)
```text
    function swapAssetToPremintedRsETH(
        address rsETH,
        address token,
        uint256 rsETHAmount
    )
        external
        nonReentrant
        onlySupportedTokenOrEth(token)
        onlyRole(OPERATOR_ROLE)
    {
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L130-159)
```text
    modifier limitDailyMint(uint256 amount, address token) {
        if (block.timestamp < startTimestamp) {
            revert MintBeforeStartTimestamp();
        }

        uint256 rsETHAmount;

        // Calculate the amount of rsETH that will be minted
        if (token == ETH_IDENTIFIER) {
            (rsETHAmount,) = viewSwapRsETHAmountAndFee(amount);
        } else {
            (rsETHAmount,) = viewSwapRsETHAmountAndFee(amount, token);
        }

        uint256 currentDay = getCurrentDay();

        // If the current day is greater than the last mint day, reset the daily mint amount
        if (currentDay > lastMintDay) {
            lastMintDay = currentDay;
            dailyMintAmount = 0;
        }

        // Check if the daily mint amount plus the amount to mint is greater than the daily mint limit
        if (dailyMintAmount + rsETHAmount > dailyMintLimit) {
            revert DailyMintLimitExceeded();
        }

        dailyMintAmount += rsETHAmount;
        _;
    }
```

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L108-137)
```text
    modifier limitDailyMint(uint256 amount, address token) {
        if (block.timestamp < startTimestamp) {
            revert MintBeforeStartTimestamp();
        }

        uint256 rsETHAmount;

        // Calculate the amount of rsETH that will be minted
        if (token == ETH_IDENTIFIER) {
            (rsETHAmount,) = viewSwapRsETHAmountAndFee(amount);
        } else {
            (rsETHAmount,) = viewSwapRsETHAmountAndFee(amount, token);
        }

        uint256 currentDay = getCurrentDay();

        // If the current day is greater than the last mint day, reset the daily mint amount
        if (currentDay > lastMintDay) {
            lastMintDay = currentDay;
            dailyMintAmount = 0;
        }

        // Check if the daily mint amount plus the amount to mint is greater than the daily mint limit
        if (dailyMintAmount + rsETHAmount > dailyMintLimit) {
            revert DailyMintLimitExceeded();
        }

        dailyMintAmount += rsETHAmount;
        _;
    }
```
