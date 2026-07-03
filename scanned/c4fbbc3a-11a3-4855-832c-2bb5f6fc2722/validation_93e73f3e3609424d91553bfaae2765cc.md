### Title
Stale Cached `rsETHPrice` Allows Depositors to Mint Excess rsETH, Stealing Yield from Existing Holders - (File: contracts/LRTDepositPool.sol)

### Summary
`LRTDepositPool.getRsETHAmountToMint` uses a cached, manually-updated `rsETHPrice` from `LRTOracle` while simultaneously reading live asset prices. When rebasing LSTs (e.g., stETH) accrue yield between oracle updates, the stale `rsETHPrice` causes new depositors to receive more rsETH than they are entitled to, diluting existing holders and stealing their unclaimed yield.

### Finding Description
`getRsETHAmountToMint` computes the rsETH to mint as:

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

`lrtOracle.getAssetPrice(asset)` reads a live price from an external price oracle (e.g., Chainlink), while `lrtOracle.rsETHPrice()` returns a **cached storage variable** that is only updated when `updateRSETHPrice()` is explicitly called.

`rsETHPrice` is computed in `_updateRsETHPrice()` as:

```solidity
uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```

Between calls to `updateRSETHPrice()`, stETH (a rebasing token) continuously increases its `balanceOf` balance. `getTotalAssetDeposits` for stETH reads `IERC20(asset).balanceOf(address(this))` directly, so the actual TVL grows in real time. However, `rsETHPrice` does not reflect this growth until explicitly updated. The formula therefore uses a stale (too-low) denominator, minting more rsETH than the depositor's contribution warrants.

There is no call to `updateRSETHPrice()` inside `depositETH` or `depositAsset` before minting.

### Impact Explanation
When stETH rebases (approximately daily at ~4% APY), the protocol's actual TVL increases but `rsETHPrice` remains at the pre-rebase value. A depositor who deposits during this window receives:

```
rsETH_minted = amount * assetPrice / rsETHPrice_stale
```

instead of the correct:

```
rsETH_minted = amount * assetPrice / rsETHPrice_actual
```

Since `rsETHPrice_stale < rsETHPrice_actual`, the depositor receives excess rsETH. When `updateRSETHPrice()` is subsequently called, the new price is computed over a larger supply (including the excess minted rsETH), permanently diluting all prior holders. The excess rsETH represents a direct transfer of unclaimed yield from existing holders to the new depositor.

**Impact: High — Theft of unclaimed yield from existing rsETH holders.**

### Likelihood Explanation
stETH rebases every ~24 hours. If `updateRSETHPrice()` is not called atomically before every deposit (it is not — it is a separate public function), any depositor can exploit the stale window. No special permissions are required; `depositAsset` and `depositETH` are open to any user. The attacker simply deposits during the window between a stETH rebase and the next `updateRSETHPrice()` call. This does not require front-running a specific transaction — it only requires depositing while the price is stale, which is a predictable recurring condition.

### Recommendation
Call `updateRSETHPrice()` (or an equivalent internal price refresh) at the start of `depositETH` and `depositAsset` before computing `rsethAmountToMint`, ensuring the price used for minting always reflects the current TVL. Alternatively, compute `rsETHPrice` on-the-fly within `getRsETHAmountToMint` rather than reading a cached storage value.

### Proof of Concept

1. Protocol state: 100 stETH deposited, 100 rsETH minted, `rsETHPrice = 1e18` (1 ETH per rsETH).
2. stETH rebases: protocol now holds stETH worth 101 ETH. Actual rsETH price = `101e18 / 100 = 1.01e18`. `rsETHPrice` in storage is still `1e18`.
3. Attacker calls `depositAsset(stETH, 10e18, 0, "")`.
4. `getRsETHAmountToMint` computes: `10e18 * 1e18 / 1e18 = 10e18` rsETH minted.
5. Correct amount should be: `10e18 * 1e18 / 1.01e18 ≈ 9.9e18` rsETH.
6. Attacker receives ~0.099 excess rsETH.
7. `updateRSETHPrice()` is called: new TVL = 111 ETH, new supply = 110 rsETH, new price = `111/110 ≈ 1.009e18`.
8. Original 100 rsETH holders now hold `100 * 1.009e18 = 100.9 ETH` worth instead of the `101 ETH` they were entitled to — ~0.1 ETH of yield was stolen by the attacker.

**Root cause (exact lines):** [1](#0-0) 

**Cached price storage variable read:** [2](#0-1) 

**Price only updated on explicit call, not on deposit:** [3](#0-2) 

**No price refresh before minting in deposit flow:** [4](#0-3) 

**`_getTotalEthInProtocol` reads live rebasing stETH balance, but this is only used inside `updateRSETHPrice`, not at deposit time:** [5](#0-4)

### Citations

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

**File:** contracts/LRTDepositPool.sol (L506-521)
```text
    function getRsETHAmountToMint(
        address asset,
        uint256 amount
    )
        public
        view
        override
        returns (uint256 rsethAmountToMint)
    {
        // setup oracle contract
        address lrtOracleAddress = lrtConfig.getContract(LRTConstants.LRT_ORACLE);
        ILRTOracle lrtOracle = ILRTOracle(lrtOracleAddress);

        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L28-28)
```text
    uint256 public override rsETHPrice;
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
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
