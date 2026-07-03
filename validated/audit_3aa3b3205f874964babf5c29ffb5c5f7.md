Audit Report

## Title
Uninitialized Cross-Chain Rate Causes Division-by-Zero, Temporarily Freezing All L2 Deposits - (File: contracts/cross-chain/CrossChainRateReceiver.sol)

## Summary
`CrossChainRateReceiver.rate` defaults to `0` at deployment and is only updated via `lzReceive()` after a cross-chain message from L1. Before that first message arrives, every L2 pool deposit reverts with a division-by-zero panic because `viewSwapRsETHAmountAndFee()` divides by the oracle rate without a zero-guard. No user funds are at risk of loss, but all deposits are completely frozen during this window.

## Finding Description
`CrossChainRateReceiver` declares `uint256 public rate` with no initializer, so it holds `0` at deployment. [1](#0-0) 

The only write path is `lzReceive()`, which requires a LayerZero message from L1 to have been sent and delivered. [2](#0-1) 

`getRate()` returns `rate` directly with no zero-check. [3](#0-2) 

All three pool variants call `viewSwapRsETHAmountAndFee()`, which fetches this rate and immediately divides by it:

- `RSETHPoolV3`: [4](#0-3) 
- `RSETHPoolNoWrapper`: [5](#0-4) 
- `RSETHPoolV3ExternalBridge`: [6](#0-5) 

In `RSETHPoolV3` and `RSETHPoolV3ExternalBridge`, the `limitDailyMint` modifier calls `viewSwapRsETHAmountAndFee()` before the deposit body executes, so the panic fires even before the amount check. [7](#0-6) 

Neither `initialize()` nor `setRSETHOracle()` validates that the oracle returns a non-zero rate: [8](#0-7) [9](#0-8) 

This is inconsistent with `addSupportedToken()`, which explicitly guards against a zero rate for token oracles: [10](#0-9) 

The same guard is present in `RSETHPoolNoWrapper.addSupportedToken()` and `RSETHPoolV3ExternalBridge._addSupportedToken()`, confirming the developers are aware of the zero-rate risk for token oracles but did not apply it to the primary `rsETHOracle` path. [11](#0-10) [12](#0-11) 

## Impact Explanation
Every call to `deposit()` (ETH or token) on any affected L2 pool reverts with an arithmetic panic (division by zero) during the window between contract deployment and receipt of the first cross-chain rate message. The pool holds no user funds at this stage, so no funds are lost, but the service is completely unavailable. This maps to **Medium – Temporary freezing of funds**.

## Likelihood Explanation
This window is a normal, unavoidable part of every new L2 pool deployment. The pool is initialized, the `CrossChainRateReceiver`-backed oracle is deployed with `rate == 0`, and a non-trivial delay exists before the first `updateRate()` → `lzReceive()` round-trip completes. Any user who attempts a deposit during this window is affected. No attacker action is required; the condition is triggered by ordinary user behavior. The window is bounded only by operational latency (minutes to hours), making it a predictable and repeatable condition on each new chain deployment.

## Recommendation
1. Add a non-zero rate check in `initialize()` and `setRSETHOracle()` for all pool variants, mirroring the guard already present in `addSupportedToken()`:
   ```solidity
   if (IOracle(_rsETHOracle).getRate() == 0) revert UnsupportedOracle();
   ```
2. Add an explicit zero-rate guard inside `viewSwapRsETHAmountAndFee()` before the division, reverting with a descriptive error rather than a bare arithmetic panic:
   ```solidity
   if (rsETHToETHrate == 0) revert UnsupportedOracle();
   ```
3. Consider initializing `CrossChainRateReceiver.rate` to a sentinel non-zero value in a constructor/initializer, or require the deployer to supply an initial rate.

## Proof of Concept
1. Deploy a fresh `CrossChainRateReceiver`-backed oracle on an L2. `rate == 0`.
2. Deploy (or upgrade) an L2 pool pointing to this oracle. `initialize()` / `setRSETHOracle()` accepts it without checking the rate.
3. Before `MultiChainRateProvider.updateRate()` is called on L1 (or before the LayerZero message is delivered), call `deposit{value: 1 ether}("ref")` on the pool.
4. Execution enters the `limitDailyMint` modifier (for `RSETHPoolV3`/`RSETHPoolV3ExternalBridge`) or directly calls `viewSwapRsETHAmountAndFee(1 ether)`:
   ```
   rsETHToETHrate = getRate()           // returns 0
   rsETHAmount = amountAfterFee * 1e18 / 0  // panic: division by zero
   ```
5. Transaction reverts. All deposits are frozen until the first cross-chain rate message arrives.

**Foundry test sketch:**
```solidity
function test_depositRevertsWhenRateIsZero() public {
    // Deploy CrossChainRateReceiver-backed oracle (rate == 0 by default)
    MockCrossChainOracle oracle = new MockCrossChainOracle(); // getRate() returns 0
    // Deploy pool pointing to oracle
    RSETHPoolV3 pool = new RSETHPoolV3();
    pool.initialize(admin, bridger, wrsETH, 0, address(oracle), true);
    // Attempt deposit before lzReceive sets a rate
    vm.expectRevert(); // arithmetic panic (division by zero)
    pool.deposit{value: 1 ether}("ref");
}
```

### Citations

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L12-13)
```text
    /// @notice Last rate updated on the receiver
    uint256 public rate;
```

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L82-99)
```text
    function lzReceive(uint16 _srcChainId, bytes memory _srcAddress, uint64, bytes calldata _payload) external {
        require(msg.sender == layerZeroEndpoint, "Sender should be lz endpoint");

        address srcAddress;
        assembly {
            srcAddress := mload(add(_srcAddress, 20))
        }

        require(_srcChainId == srcChainId, "Src chainId must be correct");
        require(srcAddress == rateProvider, "Src address must be provider");

        uint256 _rate = abi.decode(_payload, (uint256));

        rate = _rate;

        lastUpdated = block.timestamp;

        emit RateUpdated(_rate);
```

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L103-105)
```text
    function getRate() external view returns (uint256) {
        return rate;
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L96-108)
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
```

**File:** contracts/pools/RSETHPoolV3.sol (L218-231)
```text
        UtilLib.checkNonZeroAddress(_wrsETH);
        UtilLib.checkNonZeroAddress(_rsETHOracle);

        __ERC20_init("rsETH", "rsETH");
        __AccessControl_init();
        __ReentrancyGuard_init();

        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _setupRole(BRIDGER_ROLE, bridger);

        wrsETH = IERC20WrsETH(_wrsETH);
        feeBps = _feeBps;
        rsETHOracle = _rsETHOracle;
        isEthDepositEnabled = _isEthDepositEnabled;
```

**File:** contracts/pools/RSETHPoolV3.sol (L299-308)
```text
    function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L533-537)
```text
    function setRSETHOracle(address _rsETHOracle) external onlyRole(TIMELOCK_ROLE) {
        UtilLib.checkNonZeroAddress(_rsETHOracle);
        rsETHOracle = _rsETHOracle;
        emit OracleSet(_rsETHOracle);
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L548-550)
```text
        if (IOracle(oracle).getRate() == 0) {
            revert UnsupportedOracle();
        }
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L277-286)
```text
    function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
    }
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L584-586)
```text
        if (IOracle(oracle).getRate() == 0) {
            revert UnsupportedOracle();
        }
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L418-427)
```text
    function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
    }
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L893-895)
```text
        if (IOracle(oracle).getRate() == 0) {
            revert UnsupportedOracle();
        }
```
