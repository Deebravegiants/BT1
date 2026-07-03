I have the full contract. Let me analyze the exact code path.

### Title
Fee-on-Transfer Token Deposit Mints Unbacked wrsETH Based on Nominal Amount — (`contracts/pools/RSETHPoolV3ExternalBridge.sol`)

---

### Summary

`deposit(address token, uint256 amount, string referralId)` in `RSETHPoolV3ExternalBridge` calculates the wrsETH to mint using the caller-supplied `amount` parameter rather than the actual tokens received by the pool. If a fee-on-transfer ERC20 is ever listed as a supported token, the pool receives `amount − transferFee` but mints wrsETH equivalent to the full `amount`, creating unbacked supply and directly diluting every other wrsETH holder.

---

### Finding Description

The token-deposit path is:

```
deposit(token, amount, referralId)
  → safeTransferFrom(msg.sender, address(this), amount)   // pool receives amount − fee
  → viewSwapRsETHAmountAndFee(amount, token)              // uses nominal amount
  → wrsETH.mint(msg.sender, rsETHAmount)                  // mints on nominal amount
``` [1](#0-0) 

`viewSwapRsETHAmountAndFee(amount, token)` computes:

```
fee         = amount * feeBps / 10_000
amountAfterFee = amount - fee
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate
``` [2](#0-1) 

Both the pool-fee deduction and the rsETH calculation operate on the **caller-supplied `amount`**, never on the balance delta actually credited to the contract. There is no pre/post balance check anywhere in the function.

`_addSupportedToken` validates only that the token address is non-zero, is not already listed, and that its oracle returns a non-zero rate. It contains no guard against fee-on-transfer behaviour. [3](#0-2) 

---

### Impact Explanation

Every deposit with a fee-on-transfer token mints more wrsETH than the collateral backing it. The shortfall is `transferFee * tokenToETHRate / rsETHToETHrate` wrsETH per deposit. Because wrsETH is redeemable for real assets, the unbacked surplus is effectively extracted from the pool's existing collateral, constituting **direct theft of funds from other depositors** — matching the Critical scope target.

---

### Likelihood Explanation

The precondition is that a fee-on-transfer token is listed via `addSupportedToken`, which requires `TIMELOCK_ROLE`. The current production deployment supports only wstETH, which carries no transfer fee. However:

- The protocol is explicitly designed to expand its supported-token set over time (five reinitializer versions already exist, one of which added wstETH support).
- `_addSupportedToken` has no technical barrier against fee-on-transfer tokens.
- A governance proposal to add a rebasing or deflationary LST/LRT could inadvertently introduce this condition without any on-chain check catching it.

Likelihood is **low** (requires a future admin listing decision), but the impact upon exploitation is **critical** and the exploit itself is trivially executable by any user once the precondition holds.

---

### Recommendation

Measure the actual balance delta and use it for all downstream calculations:

```solidity
function deposit(address token, uint256 amount, string memory referralId)
    external nonReentrant whenNotPaused onlySupportedToken(token) limitDailyMint(amount, token)
{
    if (amount == 0) revert InvalidAmount();

    uint256 balanceBefore = IERC20(token).balanceOf(address(this));
    IERC20(token).safeTransferFrom(msg.sender, address(this), amount);
    uint256 actualReceived = IERC20(token).balanceOf(address(this)) - balanceBefore;

    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(actualReceived, token);

    feeEarnedInToken[token] += fee;
    wrsETH.mint(msg.sender, rsETHAmount);

    emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId, token);
}
```

Alternatively, explicitly prohibit fee-on-transfer tokens in `_addSupportedToken` by performing a round-trip transfer check during listing.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

import "forge-std/Test.sol";
import {RSETHPoolV3ExternalBridge} from "contracts/pools/RSETHPoolV3ExternalBridge.sol";
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";

// Mock fee-on-transfer token: 1% fee on every transfer
contract FeeToken is ERC20 {
    constructor() ERC20("FeeToken", "FT") { _mint(msg.sender, 1000e18); }
    function _transfer(address from, address to, uint256 amount) internal override {
        uint256 fee = amount / 100;          // 1% fee
        super._transfer(from, address(0), fee);
        super._transfer(from, to, amount - fee);
    }
}

contract FeeOnTransferPoC is Test {
    RSETHPoolV3ExternalBridge pool;
    FeeToken token;
    address attacker = address(0xBEEF);

    function setUp() public {
        // Deploy pool (simplified; wire up wrsETH mock, oracle mock, etc.)
        // Add FeeToken as supported token via TIMELOCK_ROLE
        // ...
    }

    function testUnbackedMint() public {
        uint256 depositAmount = 1e18;
        token.transfer(attacker, depositAmount);

        vm.startPrank(attacker);
        token.approve(address(pool), depositAmount);
        pool.deposit(address(token), depositAmount, "ref");
        vm.stopPrank();

        // Pool received 0.99e18 tokens, but minted wrsETH for 1e18
        uint256 poolBalance = token.balanceOf(address(pool));
        assertEq(poolBalance, 0.99e18);  // actual collateral

        uint256 wrsETHMinted = wrsETH.balanceOf(attacker);
        // wrsETHMinted corresponds to 1e18 tokens worth — exceeds actual collateral
        // Pool is undercollateralised by 1% of deposit value
        assertTrue(wrsETHMinted > poolBalance * tokenToETHRate / rsETHToETHrate);
    }
}
```

### Citations

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L403-409)
```text
        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        wrsETH.mint(msg.sender, rsETHAmount);
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L442-452)
```text
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // rate of token in ETH
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L882-901)
```text
    function _addSupportedToken(address token, address oracle, address bridge) internal {
        UtilLib.checkNonZeroAddress(token);
        UtilLib.checkNonZeroAddress(oracle);
        UtilLib.checkNonZeroAddress(bridge);

        if (supportedTokenOracle[token] != address(0)) {
            revert AlreadySupportedToken();
        }
        if (tokenBridge[token] != address(0)) {
            revert AlreadySupportedToken();
        }
        if (IOracle(oracle).getRate() == 0) {
            revert UnsupportedOracle();
        }
        supportedTokenList.push(token);
        supportedTokenOracle[token] = oracle;
        tokenBridge[token] = bridge;

        emit AddSupportedToken(token, oracle, bridge);
    }
```
