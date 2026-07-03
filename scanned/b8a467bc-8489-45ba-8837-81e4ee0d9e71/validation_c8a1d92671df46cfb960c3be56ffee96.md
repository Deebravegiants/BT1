### Title
Unbounded `referralId` String Enables Gas Exhaustion and Temporary Deposit Freezing - (`contracts/pools/RSETHPoolV3.sol`)

---

### Summary

Both `deposit` overloads in `RSETHPoolV3` accept a `string memory referralId` parameter with no length bound. Because the string is copied into memory and emitted verbatim in a log, gas consumption scales linearly with its length. An unprivileged caller can craft a single deposit with a maximally-sized `referralId` to consume nearly the entire L2 block gas budget, preventing any other deposit from being included in that block.

---

### Finding Description

`RSETHPoolV3.deposit(string memory referralId)` and `RSETHPoolV3.deposit(address, uint256, string memory referralId)` both accept an arbitrary-length string that is used exclusively in an event emission:

```solidity
// contracts/pools/RSETHPoolV3.sol line 264
emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);

// contracts/pools/RSETHPoolV3.sol line 292
emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId, token);
```

There is no length validation anywhere in the contract or its modifiers. A grep across the entire repository for `referralId.length`, `bytes(referralId)`, or any `MAX_REFERRAL` constant returns zero results — confirming the absence of any guard. [1](#0-0) [2](#0-1) 

Gas cost breakdown for a string of length `L` bytes:

| Component | Cost |
|---|---|
| Calldata (non-zero bytes) | `16 * L` gas |
| Memory allocation | `3 * ceil(L/32)` gas + quadratic expansion term |
| `LOG` event data | `8 * L` gas |

For `L = 100 000` bytes, calldata + log alone costs ~2.4M gas. On an L2 with a 30M gas block limit, a string of ~1.5 MB saturates the block. On L2s where gas prices are fractions of a cent per unit, the ETH cost to the attacker is negligible.

The `nonReentrant`, `whenNotPaused`, and `limitDailyMint` modifiers provide no protection against this — they execute before the string is processed and do not inspect its length. [3](#0-2) 

---

### Impact Explanation

**Medium — Unbounded gas consumption / Temporary freezing of deposits.**

An attacker can repeatedly submit one deposit per block with a maximally-sized `referralId`, consuming the block's gas budget and leaving no room for legitimate deposit transactions. Deposits are temporarily frozen for the duration of the attack. No admin action is required to execute this; the attacker only needs to be a normal depositor.

---

### Likelihood Explanation

**Low-Medium.** The attack is economically viable on L2 chains (where this contract is deployed) because gas prices are orders of magnitude cheaper than on L1. The attacker's ETH deposit cost is 1 wei per block; the gas cost, while real, is low on L2. The attack requires no special privileges, no front-running, and no external dependency.

---

### Recommendation

Add a maximum length check on `referralId` in both `deposit` overloads:

```solidity
uint256 private constant MAX_REFERRAL_ID_LENGTH = 128; // or similar reasonable bound

function deposit(string memory referralId) external payable ... {
    if (bytes(referralId).length > MAX_REFERRAL_ID_LENGTH) revert ReferralIdTooLong();
    ...
}

function deposit(address token, uint256 amount, string memory referralId) external ... {
    if (bytes(referralId).length > MAX_REFERRAL_ID_LENGTH) revert ReferralIdTooLong();
    ...
}
```

This fix should be applied consistently to all pool variants (`RSETHPoolV2`, `RSETHPoolV3ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`, etc.) that share the same pattern.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// Fork test (local/private testnet only)
// 1. Deploy RSETHPoolV3 with isEthDepositEnabled = true
// 2. Record block.gasleft() before attacker tx
// 3. Attacker calls: pool.deposit{value: 1 wei}(string(new bytes(500_000)))
// 4. Record block.gasleft() after attacker tx
// 5. Assert: remaining gas < gas required for a normal deposit (~80_000 gas)
// 6. Assert: attacker ETH cost = 1 wei (plus gas fees paid to sequencer)

function testBlockStuffing() public {
    uint256 gasStart = gasleft();
    
    // Attacker: 500KB referralId
    bytes memory bigId = new bytes(500_000);
    pool.deposit{value: 1 wei}(string(bigId));
    
    uint256 gasUsed = gasStart - gasleft();
    // gasUsed >> 8_000_000 (500_000 bytes * 16 calldata + 8 log = 12M gas)
    // A normal deposit costs ~80_000 gas — insufficient gas remains in block
    assertGt(gasUsed, 8_000_000);
}
``` [4](#0-3)

### Citations

**File:** contracts/pools/RSETHPoolV3.sol (L150-153)
```text
    event SwapOccurred(address indexed user, uint256 rsETHAmount, uint256 fee, string referralId);
    event SwapOccurred(
        address indexed user, uint256 rsETHAmount, uint256 fee, string referralId, address indexed token
    );
```

**File:** contracts/pools/RSETHPoolV3.sol (L246-265)
```text
    function deposit(string memory referralId)
        external
        payable
        nonReentrant
        whenNotPaused
        limitDailyMint(msg.value, ETH_IDENTIFIER)
    {
        if (!isEthDepositEnabled) revert EthDepositDisabled();
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L271-293)
```text
    function deposit(
        address token,
        uint256 amount,
        string memory referralId
    )
        external
        nonReentrant
        whenNotPaused
        onlySupportedToken(token)
        limitDailyMint(amount, token)
    {
        if (amount == 0) revert InvalidAmount();

        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId, token);
    }
```
