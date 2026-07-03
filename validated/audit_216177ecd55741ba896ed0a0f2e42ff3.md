### Title
Unimplemented `getLatestRate()` Stub Silently Returns Zero, Enabling Deposit Freeze on L2 — (`contracts/cross-chain/CrossChainRateProvider.sol`, `contracts/cross-chain/MultiChainRateProvider.sol`)

---

### Summary

Both `CrossChainRateProvider` and `MultiChainRateProvider` declare `getLatestRate()` as a `virtual` function with an **empty body**, making it a silent stub that returns `0` by default. Because the body is present (even if empty), Solidity does **not** force concrete subclasses to override it. If a deployed subclass inherits the stub, every call to `updateRate()` broadcasts a rate of `0` to all L2 receivers via LayerZero. Any L2 pool (`RSETHPoolV3`) consuming that rate will then revert on every deposit due to division by zero, freezing all L2 deposits until the rate is corrected.

---

### Finding Description

`CrossChainRateProvider.getLatestRate()` is declared as:

```solidity
function getLatestRate() public view virtual returns (uint256) { }
``` [1](#0-0) 

`MultiChainRateProvider.getLatestRate()` is identically declared:

```solidity
function getLatestRate() public view virtual returns (uint256) { }
``` [2](#0-1) 

Both abstract contracts call this stub inside `updateRate()`:

```solidity
function updateRate() external payable nonReentrant {
    uint256 latestRate = getLatestRate();   // returns 0 if not overridden
    rate = latestRate;
    ...
    ILayerZeroEndpoint(layerZeroEndpoint).send{ value: msg.value }(
        dstChainId, remoteAndLocalAddresses, _payload, ...
    );
}
``` [3](#0-2) 

Because the function body is `{ }` (not absent), Solidity treats it as implemented. A concrete subclass that forgets to override `getLatestRate()` compiles and deploys without error, but every `updateRate()` call encodes and broadcasts `0` as the rsETH/ETH rate to every registered L2 receiver.

On L2, `RSETHPoolV3.getRate()` reads from the oracle that was just updated to `0`:

```solidity
function getRate() public view returns (uint256) {
    return IOracle(rsETHOracle).getRate();
}
``` [4](#0-3) 

`viewSwapRsETHAmountAndFee` then performs:

```solidity
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;  // division by zero → revert
``` [5](#0-4) 

This revert propagates through both `deposit(string)` (ETH) and `deposit(address,uint256,string)` (ERC-20), as both call `viewSwapRsETHAmountAndFee` inside the `limitDailyMint` modifier before any state change. [6](#0-5) 

---

### Impact Explanation

All L2 deposits via `RSETHPoolV3` revert with a division-by-zero panic the moment the zero rate is received. No user can mint wrsETH until the rate is corrected by a subsequent `updateRate()` call from a properly implemented subclass or an admin intervention. This constitutes **temporary freezing of funds** (user ETH/LSTs are locked in the pool, unable to be converted to wrsETH).

---

### Likelihood Explanation

The `virtual` function with an empty body is a latent trap: Solidity emits no warning, the contract compiles cleanly, and the bug is invisible until `updateRate()` is called in production. Any concrete subclass that omits the override — whether through developer oversight or a future upgrade — silently activates the freeze. The `updateRate()` function is `external payable` with no access control, so any caller (including an unprivileged user) can trigger the broadcast of the zero rate.

---

### Recommendation

Remove the empty body from `getLatestRate()` in both abstract contracts so that Solidity enforces implementation in every concrete subclass:

```solidity
// Before (silent stub):
function getLatestRate() public view virtual returns (uint256) { }

// After (truly abstract — compile-time enforcement):
function getLatestRate() public view virtual returns (uint256);
``` [7](#0-6) [8](#0-7) 

---

### Proof of Concept

1. Deploy a concrete subclass of `CrossChainRateProvider` (or `MultiChainRateProvider`) that does **not** override `getLatestRate()`. The contract compiles and deploys without error.
2. Call `updateRate()` with sufficient ETH for LayerZero fees. The function executes: `latestRate = getLatestRate()` → `0`; `rate = 0`; LayerZero message sent encoding `0`.
3. The L2 rate receiver processes the message and updates the rsETH oracle to return `0`.
4. Any user calling `RSETHPoolV3.deposit(referralId)` or `RSETHPoolV3.deposit(token, amount, referralId)` triggers `limitDailyMint` → `viewSwapRsETHAmountAndFee` → `amountAfterFee * 1e18 / 0` → EVM division-by-zero revert.
5. All L2 deposits are frozen until a corrected rate is broadcast.

### Citations

**File:** contracts/cross-chain/CrossChainRateProvider.sol (L85-101)
```text
    function updateRate() external payable nonReentrant {
        uint256 latestRate = getLatestRate();

        bytes memory remoteAndLocalAddresses = abi.encodePacked(rateReceiver, address(this));

        rate = latestRate;

        lastUpdated = block.timestamp;

        bytes memory _payload = abi.encode(latestRate);

        ILayerZeroEndpoint(layerZeroEndpoint).send{ value: msg.value }(
            dstChainId, remoteAndLocalAddresses, _payload, payable(msg.sender), address(0x0), bytes("")
        );

        emit RateUpdated(rate);
    }
```

**File:** contracts/cross-chain/CrossChainRateProvider.sol (L103-104)
```text
    /// @notice Returns the latest rate
    function getLatestRate() public view virtual returns (uint256) { }
```

**File:** contracts/cross-chain/MultiChainRateProvider.sol (L180-181)
```text
    /// @notice Returns the latest rate
    function getLatestRate() public view virtual returns (uint256) { }
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

**File:** contracts/pools/RSETHPoolV3.sol (L235-237)
```text
    function getRate() public view returns (uint256) {
        return IOracle(rsETHOracle).getRate();
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L307-307)
```text
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```
