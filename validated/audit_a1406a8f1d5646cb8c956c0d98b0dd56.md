### Title
Stale `rsETHPrice` Used in Deposit Minting Calculation Without Prior Refresh - (File: contracts/LRTDepositPool.sol)

### Summary

`LRTDepositPool.depositETH()` and `depositAsset()` compute the rsETH amount to mint using `lrtOracle.rsETHPrice()`, a stored state variable that is only updated when `updateRSETHPrice()` is explicitly called. Neither deposit path refreshes this value before using it. When the stored price lags behind the true current price (which rises as restaking yield accrues), depositors receive more rsETH than they are entitled to, diluting all existing rsETH holders.

### Finding Description

`LRTDepositPool.getRsETHAmountToMint()` divides the deposited asset value by `lrtOracle.rsETHPrice()`:

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

`rsETHPrice` is a plain storage variable in `LRTOracle` that is only written inside `_updateRsETHPrice()`, which is invoked by the public `updateRSETHPrice()` or the manager-only `updateRSETHPriceAsManager()`. Neither `depositETH()` nor `depositAsset()` calls either of these before computing the mint amount. [1](#0-0) [2](#0-1) [3](#0-2) 

As restaking yield accrues, the true rsETH/ETH rate rises continuously. `rsETHPrice` only catches up when a keeper (or any caller) explicitly invokes `updateRSETHPrice()`. In the window between two updates, the stored price is lower than the true rate. Because the mint formula is `assetValue / rsETHPrice`, a lower denominator produces a larger rsETH output. The depositor receives more rsETH than their proportional share of the protocol's TVL warrants. [4](#0-3) [5](#0-4) 

### Impact Explanation

Every rsETH token represents a claim on a fixed fraction of the protocol's total ETH. When a depositor mints rsETH at a stale (understated) price, they receive a larger fraction than their deposit justifies. This fraction is taken from existing holders: the same total ETH is now split among more rsETH tokens, so each pre-existing token is worth less ETH than it was before the deposit. The loss to existing holders equals the excess rsETH minted multiplied by the true rsETH price — a direct, quantifiable theft of accrued yield.

**Impact class:** High — theft of unclaimed yield from existing rsETH holders.

### Likelihood Explanation

`updateRSETHPrice()` is not called atomically with deposits; it is driven by an off-chain keeper on a periodic schedule. Any depositor who monitors the chain can observe that the stored `rsETHPrice` has not been refreshed recently and deposit before the next update. The window is predictable and repeatable. No special privilege is required; any address can call `depositETH()` or `depositAsset()`. [3](#0-2) 

### Recommendation

Invoke `_updateRsETHPrice()` (or the public `updateRSETHPrice()`) at the start of `_beforeDeposit()` before reading `rsETHPrice`, so that every deposit uses the freshest possible exchange rate. Alternatively, enforce a maximum staleness window and revert if `rsETHPrice` has not been updated within that window.

### Proof of Concept

1. Protocol has 1000 ETH TVL and 1000 rsETH outstanding → true price = 1.01 ETH/rsETH after yield accrual, but stored `rsETHPrice` = 1.00 ETH/rsETH (stale, not yet updated).
2. Attacker calls `depositETH{value: 10 ETH}(0, "")`.
3. `getRsETHAmountToMint` computes: `10e18 * 1e18 / 1e18 = 10 rsETH` (using stale price of 1.00).
4. True fair share at price 1.01: `10 / 1.01 ≈ 9.9 rsETH`.
5. Attacker receives 10 rsETH instead of 9.9 rsETH — an excess of ~0.1 rsETH (~0.101 ETH at true price).
6. Existing 1000 rsETH holders collectively lose that 0.101 ETH of accrued yield.
7. Attacker immediately calls `updateRSETHPrice()` (public, no access control) to lock in the new price, then repeats on the next accrual cycle. [6](#0-5) [7](#0-6)

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

**File:** contracts/LRTDepositPool.sol (L648-670)
```text
    function _beforeDeposit(
        address asset,
        uint256 depositAmount,
        uint256 minRSETHAmountExpected
    )
        private
        view
        returns (uint256 rsethAmountToMint)
    {
        if (depositAmount == 0 || depositAmount < minAmountToDeposit) {
            revert InvalidAmountToDeposit();
        }

        if (_checkIfDepositAmountExceedesCurrentLimit(asset, depositAmount)) {
            revert MaximumDepositLimitReached();
        }

        rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);

        if (rsethAmountToMint < minRSETHAmountExpected) {
            revert MinimumAmountToReceiveNotMet();
        }
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

**File:** contracts/LRTOracle.sol (L313-315)
```text
        rsETHPrice = newRsETHPrice;

        emit RsETHPriceUpdate(rsETHPrice, previousPrice);
```
