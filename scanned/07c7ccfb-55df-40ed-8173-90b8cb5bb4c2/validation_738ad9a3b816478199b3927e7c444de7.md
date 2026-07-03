### Title
Unprivileged Caller Can Trigger Protocol-Wide Pause via Transient Chainlink Price Dip — (`contracts/LRTOracle.sol`)

### Summary

`updateRSETHPrice()` is a public, permissionless function. Its internal logic pauses `LRTOracle`, `LRTDepositPool`, and `LRTWithdrawalManager` simultaneously whenever the computed rsETH price falls below `highestRsethPrice` by more than `pricePercentageLimit`. Because the price is derived from live Chainlink spot feeds, a transient feed dip (e.g., stETH/ETH during a depeg scare) is sufficient to trigger the pause. Any address — including `address(1)` — can call the function at the right moment and freeze all user-facing operations until an admin manually unpauses each contract.

### Finding Description

`updateRSETHPrice()` carries only the `whenNotPaused` modifier: [1](#0-0) 

Inside `_updateRsETHPrice()`, the downside-protection block unconditionally pauses three contracts when the price drop exceeds the configured threshold: [2](#0-1) 

The price used for comparison is the live Chainlink spot price, fetched through `_getTotalEthInProtocol()` → `getAssetPrice()` → `IPriceFetcher.getAssetPrice()`: [3](#0-2) 

`LRTDepositPool.pause()` and `LRTWithdrawalManager.pause()` both require `PAUSER_ROLE`. For the oracle's internal calls to succeed, `LRTOracle` must hold that role on both contracts — which is the intended deployment configuration given the code explicitly calls them. Once paused:

- `depositETH()` / `depositAsset()` revert via `whenNotPaused` on `LRTDepositPool` [4](#0-3) 
- Withdrawal initiations and queue unlocks revert via `whenNotPaused` on `LRTWithdrawalManager` [5](#0-4) 

Unpausing requires an admin to call `unpause()` on each of the three contracts individually. [6](#0-5) 

### Impact Explanation

All user deposits and withdrawal initiations are frozen until admin intervention. This is **temporary freezing of funds** (Medium). No funds are lost, but users cannot enter or exit the protocol for the duration of the pause.

### Likelihood Explanation

- The attacker needs no role, no capital, and no special setup — just a call to a public function.
- Chainlink stETH/ETH spot feeds have historically deviated >1% intraday during volatility events (e.g., the June 2022 stETH depeg, the March 2023 banking crisis).
- `pricePercentageLimit` is admin-configurable; at 1% (1e16) the threshold is easily breached by normal market noise.
- The attacker can monitor the mempool or the Chainlink feed off-chain and call `updateRSETHPrice()` precisely when the feed is at its lowest point within a candle.

### Recommendation

1. **Restrict the caller**: Add `onlyLRTManager` (or a dedicated keeper role) to `updateRSETHPrice()`, keeping the permissionless path only for price reads.
2. **Use a TWAP or circuit-breaker cooldown**: Require the depressed price to persist for N blocks before triggering a pause, preventing single-block feed anomalies from halting the protocol.
3. **Separate the pause trigger from the price update**: Emit an event and let a privileged keeper decide whether to pause, rather than auto-pausing inside a public function.

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

// Fork test (Foundry) — run against a mainnet fork
// Assumes: pricePercentageLimit = 1e16 (1%), highestRsethPrice already set

contract AuditPoC is Test {
    LRTOracle oracle = LRTOracle(<deployed_oracle>);
    LRTDepositPool pool = LRTDepositPool(<deployed_pool>);
    LRTWithdrawalManager wm = LRTWithdrawalManager(<deployed_wm>);

    function testUnprivilegedPauseTrigger() public {
        // 1. Mock the stETH/ETH Chainlink feed to return a price 2% below
        //    the current highestRsethPrice (simulating a transient depeg).
        vm.mockCall(
            <chainlink_steth_feed>,
            abi.encodeWithSignature("latestRoundData()"),
            abi.encode(0, <depressed_price>, 0, block.timestamp, 0)
        );

        // 2. Any unprivileged address calls the public function.
        vm.prank(address(1));
        oracle.updateRSETHPrice();

        // 3. All three contracts are now paused.
        assertTrue(oracle.paused());
        assertTrue(pool.paused());
        assertTrue(wm.paused());

        // 4. User operations revert.
        vm.expectRevert();
        pool.depositETH{value: 1 ether}(0, "");
    }
}
```

### Citations

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L143-146)
```text
    function unpause() external whenPaused onlyLRTAdmin {
        paused = false;
        emit Unpaused(msg.sender);
    }
```

**File:** contracts/LRTOracle.sol (L270-282)
```text
        if (newRsETHPrice < highestRsethPrice) {
            uint256 diff = highestRsethPrice - newRsETHPrice;
            // normalizing to 1e18
            bool isPriceDecreaseOffLimit =
                pricePercentageLimit > 0 && diff > pricePercentageLimit.mulWad(highestRsethPrice);

            // if price decrease is off limit, pause the protocol (unless it's already paused)
            if (isPriceDecreaseOffLimit) {
                if (!lrtDepositPool.paused()) lrtDepositPool.pause();
                if (!withdrawalManager.paused()) withdrawalManager.pause();
                _pause();
                return;
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

**File:** contracts/LRTDepositPool.sol (L76-93)
```text
    function depositETH(
        uint256 minRSETHAmountExpected,
        string calldata referralId
    )
        external
        payable
        nonReentrant
        whenNotPaused
        onlySupportedAsset(LRTConstants.ETH_TOKEN)
    {
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(LRTConstants.ETH_TOKEN, msg.value, minRSETHAmountExpected);

        // interactions
        _mintRsETH(rsethAmountToMint);

        emit ETHDeposit(msg.sender, msg.value, rsethAmountToMint, referralId);
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L26-31)
```text
contract LRTWithdrawalManager is
    ILRTWithdrawalManager,
    LRTConfigRoleChecker,
    PausableUpgradeable,
    ReentrancyGuardUpgradeable
{
```
