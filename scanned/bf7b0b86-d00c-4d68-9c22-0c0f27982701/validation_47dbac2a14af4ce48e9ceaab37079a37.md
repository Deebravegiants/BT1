### Title
Stale `rsETHPrice` Used in Deposit and Instant-Withdrawal Calculations Without Prior Oracle Update - (File: `contracts/LRTDepositPool.sol`, `contracts/LRTWithdrawalManager.sol`)

---

### Summary
`LRTOracle.rsETHPrice` is a cached storage variable that must be explicitly refreshed by calling `updateRSETHPrice()`. Neither `depositETH()`/`depositAsset()` in `LRTDepositPool` nor `instantWithdrawal()` in `LRTWithdrawalManager` call `updateRSETHPrice()` before reading `rsETHPrice`. As a result, both minting and instant-withdrawal calculations can execute against a stale exchange rate, enabling a depositor to receive more rsETH than the current protocol value warrants, stealing accrued yield from existing holders.

---

### Finding Description

`LRTOracle` stores the rsETH/ETH exchange rate in the public state variable `rsETHPrice`. [1](#0-0) 

This value is only updated when `updateRSETHPrice()` (or its internal helper `_updateRsETHPrice()`) is explicitly called. [2](#0-1) 

`LRTDepositPool.getRsETHAmountToMint()` reads `lrtOracle.rsETHPrice()` directly without triggering an update: [3](#0-2) 

This function is called unconditionally inside both `depositETH()` and `depositAsset()`: [4](#0-3) [5](#0-4) 

Likewise, `LRTWithdrawalManager.instantWithdrawal()` calls `getExpectedAssetAmount()`, which also reads the stale `rsETHPrice` without refreshing it: [6](#0-5) [7](#0-6) 

---

### Impact Explanation

**Classification: High — Theft of unclaimed yield.**

`rsETHPrice` increases monotonically as staking rewards accrue in the protocol. Between oracle updates, the stored price is lower than the true current value. When a depositor calls `depositETH()` or `depositAsset()` against a stale (lower) `rsETHPrice`:

```
rsethAmountToMint = (depositAmount × assetPrice) / rsETHPrice
```

A lower denominator produces a larger `rsethAmountToMint`. The new depositor receives more rsETH than the current protocol value justifies. Because rsETH is a share token backed by a fixed pool of assets, over-minting dilutes every existing holder's proportional claim — their accrued yield is transferred to the late depositor.

For `instantWithdrawal()`, if `rsETHPrice` is stale and higher than the actual current value (e.g., after a slashing event not yet reflected in the oracle), the user redeems rsETH for more underlying assets than they are entitled to, directly draining the vault.

---

### Likelihood Explanation

`updateRSETHPrice()` is a separate, permissionless transaction that is not atomically coupled to any deposit or withdrawal. In normal operation, rewards accrue continuously while the oracle is updated periodically (off-chain keeper or manual call). There will always be a window — potentially hours or days — during which `rsETHPrice` is stale. Any depositor can exploit this window without any special privilege. [2](#0-1) 

---

### Recommendation

Call `updateRSETHPrice()` (or an equivalent internal helper) at the start of `depositETH()`, `depositAsset()`, and `instantWithdrawal()` before any exchange-rate-dependent calculation is performed. This mirrors the fix described in the referenced report: explicitly accrue/update the rate before using it.

---

### Proof of Concept

1. Rewards accrue for 24 hours; `updateRSETHPrice()` has not been called. Suppose the true rsETH price is `1.05 ETH` but the stored `rsETHPrice` is `1.00 ETH`.
2. Attacker calls `depositETH{ value: 100 ether }(0, "")`.
3. `getRsETHAmountToMint` computes: `(100e18 × 1e18) / 1.00e18 = 100 rsETH`.
4. True fair amount at current price: `100e18 / 1.05e18 ≈ 95.24 rsETH`.
5. Attacker receives `≈ 4.76 rsETH` more than entitled — representing the yield accrued by all existing holders since the last oracle update.
6. After `updateRSETHPrice()` is called, the attacker's rsETH is worth `100 × 1.05 = 105 ETH` while they only deposited `100 ETH`, extracting `≈ 5 ETH` of yield from existing holders. [8](#0-7) [9](#0-8)

### Citations

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

**File:** contracts/LRTDepositPool.sol (L76-92)
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
```

**File:** contracts/LRTDepositPool.sol (L111-111)
```text
        uint256 rsethAmountToMint = _beforeDeposit(asset, depositAmount, minRSETHAmountExpected);
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

**File:** contracts/LRTWithdrawalManager.sol (L228-228)
```text
        uint256 assetAmountUnlocked = getExpectedAssetAmount(asset, rsETHUnstaked);
```

**File:** contracts/LRTWithdrawalManager.sol (L590-594)
```text
        ILRTOracle lrtOracle = ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE));

        // calculate underlying asset amount to receive based on rsETH amount and asset exchange rate
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
    }
```
