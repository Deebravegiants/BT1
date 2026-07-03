Audit Report

## Title
`_beforeDeposit` Allows Zero rsETH Minting When `minRSETHAmountExpected = 0` — Depositor Loses Assets — (File: contracts/LRTDepositPool.sol)

## Summary

`getRsETHAmountToMint` uses integer division, which truncates to zero when `amount * assetPrice < rsETHPrice`. `_beforeDeposit` only guards against `rsethAmountToMint < minRSETHAmountExpected`, so when a caller passes `minRSETHAmountExpected = 0`, the check `0 < 0` is false and execution continues. The depositor's ETH or LST is absorbed into the protocol while `_mintRsETH(0)` mints nothing in return.

## Finding Description

`getRsETHAmountToMint` (L506–521) computes:

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

This is Solidity integer division. For any `amount` where `amount * assetPrice < rsETHPrice`, the result is `0`.

`_beforeDeposit` (L648–670) then performs:

```solidity
rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);

if (rsethAmountToMint < minRSETHAmountExpected) {
    revert MinimumAmountToReceiveNotMet();
}
```

There is no `require(rsethAmountToMint > 0)`. When `minRSETHAmountExpected = 0` (a valid caller-supplied argument), the condition `0 < 0` evaluates to `false` and no revert occurs.

`minAmountToDeposit` is declared as a storage variable (L30) and is never set in `initialize` (L45–52), so it defaults to `0`. The check `depositAmount == 0 || depositAmount < minAmountToDeposit` (L657) therefore passes for any non-zero `depositAmount`.

For `depositETH` (L76–93), `msg.value` is already in the contract before `_mintRsETH(0)` is called. For `depositAsset` (L99–118), `safeTransferFrom` pulls the LST before `_mintRsETH(0)`. In both cases the depositor's funds are absorbed into protocol TVL while they receive zero rsETH.

## Impact Explanation

**Low — Contract fails to deliver promised returns.**

A depositor who calls `depositETH` or `depositAsset` with `minRSETHAmountExpected = 0` and a dust-level deposit amount receives zero rsETH while their ETH or LST is permanently added to protocol TVL, benefiting all existing rsETH holders. The depositor has no recovery path. The protocol itself does not lose value; only the individual depositor does. This matches the allowed Low impact: *"Contract fails to deliver promised returns, but doesn't lose value."*

## Likelihood Explanation

- `minAmountToDeposit` defaults to `0` and is only settable by admin; in the default deployment state any non-zero dust deposit is accepted.
- rsETHPrice grows above `1e18` as yield accrues, raising the zero-mint threshold over time.
- Any caller who omits or zeroes `minRSETHAmountExpected` — including integrating contracts that do not implement slippage protection — is silently vulnerable.
- No privileged role, front-running, or external oracle manipulation is required; the condition is reachable by any unprivileged depositor in normal protocol operation.

## Recommendation

Add an explicit zero-share guard immediately after computing `rsethAmountToMint` in `_beforeDeposit`:

```solidity
rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);

if (rsethAmountToMint == 0) {
    revert ZeroRsETHMinted();
}

if (rsethAmountToMint < minRSETHAmountExpected) {
    revert MinimumAmountToReceiveNotMet();
}
```

This ensures no depositor can lose assets while receiving zero shares, regardless of the `minRSETHAmountExpected` argument supplied.

## Proof of Concept

Assume:
- `rsETHPrice = 1.05e18` (5% yield accrued)
- `assetPrice(ETH) = 1e18`
- `minAmountToDeposit = 0` (default, never set in `initialize`)

Call sequence:
```
depositETH{value: 1}(minRSETHAmountExpected: 0, referralId: "")
```

Step-by-step execution:
1. `_beforeDeposit(ETH_TOKEN, 1, 0)` is called (L87).
2. `depositAmount (1) == 0` → false; `1 < minAmountToDeposit (0)` → false → passes (L657).
3. `getRsETHAmountToMint(ETH, 1)` → `(1 * 1e18) / 1.05e18 = 0` (integer truncation) (L520).
4. `rsethAmountToMint (0) < minRSETHAmountExpected (0)` → `false` → no revert (L667).
5. `_mintRsETH(0)` → `IRSETH(rsethToken).mint(msg.sender, 0)` → depositor receives 0 rsETH (L686–689).
6. The 1 wei ETH remains in the deposit pool, increasing TVL for all existing rsETH holders.

**Foundry fuzz test sketch:**
```solidity
function testFuzz_zeroMintOnDustDeposit(uint256 rsethPrice) public {
    rsethPrice = bound(rsethPrice, 1e18 + 1, 2e18); // rsETH appreciated
    oracle.setRsETHPrice(rsethPrice);
    oracle.setAssetPrice(ETH, 1e18);
    // depositAmount = 1 wei, minRSETHAmountExpected = 0
    vm.deal(user, 1);
    vm.prank(user);
    depositPool.depositETH{value: 1}(0, "");
    assertEq(rseth.balanceOf(user), 0); // user receives nothing
    assertEq(address(depositPool).balance, 1); // ETH absorbed into TVL
}
``` [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6)

### Citations

**File:** contracts/LRTDepositPool.sol (L29-31)
```text
    uint256 public maxNodeDelegatorLimit;
    uint256 public minAmountToDeposit;

```

**File:** contracts/LRTDepositPool.sol (L45-52)
```text
    function initialize(address lrtConfigAddr) external initializer {
        UtilLib.checkNonZeroAddress(lrtConfigAddr);
        __Pausable_init();
        __ReentrancyGuard_init();
        maxNodeDelegatorLimit = 10;
        lrtConfig = ILRTConfig(lrtConfigAddr);
        emit UpdatedLRTConfig(lrtConfigAddr);
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

**File:** contracts/LRTDepositPool.sol (L99-118)
```text
    function depositAsset(
        address asset,
        uint256 depositAmount,
        uint256 minRSETHAmountExpected,
        string calldata referralId
    )
        external
        nonReentrant
        whenNotPaused
        onlySupportedERC20Token(asset)
    {
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(asset, depositAmount, minRSETHAmountExpected);

        // interactions
        IERC20(asset).safeTransferFrom(msg.sender, address(this), depositAmount);
        _mintRsETH(rsethAmountToMint);

        emit AssetDeposit(msg.sender, asset, depositAmount, rsethAmountToMint, referralId);
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

**File:** contracts/LRTDepositPool.sol (L684-690)
```text
    /// @dev private function to mint rseth
    /// @param rsethAmountToMint Amount of rseth minted
    function _mintRsETH(uint256 rsethAmountToMint) private {
        address rsethToken = lrtConfig.rsETH();
        // mint rseth for user
        IRSETH(rsethToken).mint(msg.sender, rsethAmountToMint);
    }
```
