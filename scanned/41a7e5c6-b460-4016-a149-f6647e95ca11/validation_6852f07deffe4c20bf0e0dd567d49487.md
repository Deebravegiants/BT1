### Title
Zero-Amount wrsETH Mint on 100% Fee Silently Drains Depositor ETH — (`contracts/pools/RSETHPoolV2NBA.sol`)

### Summary

`setFeeBps` permits `feeBps = 10_000` (off-by-one in its guard), and `deposit` has no post-calculation check that `rsETHAmount > 0`. When `feeBps == 10_000`, the full ETH principal is routed to `feeEarnedInETH` while `wrsETH.mint(msg.sender, 0)` is called silently — OZ `_mint(to, 0)` is a no-op — leaving the depositor with zero wrsETH and no revert.

---

### Finding Description

**`setFeeBps` off-by-one:** [1](#0-0) 

The guard is `_feeBps > 10_000`, so `feeBps = 10_000` (100%) is accepted.

**Fee calculation with `feeBps = 10_000`:** [2](#0-1) 

- `fee = amount * 10_000 / 10_000 = amount`
- `amountAfterFee = amount - amount = 0`
- `rsETHAmount = 0 * 1e18 / rate = 0`

**`deposit` does not guard against `rsETHAmount == 0`:** [3](#0-2) 

`feeEarnedInETH += fee` absorbs the full ETH, then `wrsETH.mint(msg.sender, 0)` is called.

**`RsETHTokenWrapper.mint` with amount 0 does not revert:** [4](#0-3) 

OZ `ERC20Upgradeable._mint(to, 0)` emits a `Transfer(address(0), to, 0)` event and returns without reverting. The transaction succeeds, `SwapOccurred` is emitted with `rsETHAmount = 0`, and the depositor's ETH is permanently locked in the contract as "fees."

---

### Impact Explanation

A depositor calling `deposit{value: V}()` while `feeBps == 10_000`:
- Loses `V` ETH (credited to `feeEarnedInETH`, withdrawable only by `BRIDGER_ROLE`)
- Receives 0 wrsETH
- Transaction does not revert; no on-chain signal of failure beyond the event values

This is **direct, permanent loss of user principal** — Critical impact.

---

### Likelihood Explanation

`setFeeBps` is callable by `DEFAULT_ADMIN_ROLE`. The off-by-one means an admin can reach this state either by mistake (intending to set a high-but-not-total fee) or deliberately. No attacker key compromise is required; the contract's own validation permits the value. Any deposit made while this fee is active is silently drained.

---

### Recommendation

1. **Fix the off-by-one in `setFeeBps`:** change `> 10_000` to `>= 10_000` (or define a lower maximum, e.g. 1_000 bps).
2. **Add a zero-output guard in `deposit`:** revert if `rsETHAmount == 0` after the fee calculation.

```solidity
// setFeeBps fix
if (_feeBps >= 10_000) revert InvalidFeeAmount();

// deposit fix
(uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
if (rsETHAmount == 0) revert InvalidAmount();
```

---

### Proof of Concept

```solidity
// 1. Admin sets feeBps to 10_000 (passes the > 10_000 guard)
pool.setFeeBps(10_000);

// 2. User deposits 1 ETH
pool.deposit{value: 1 ether}("");

// 3. Assertions
assert(wrsETH.balanceOf(depositor) == 0);       // depositor got nothing
assert(pool.feeEarnedInETH() == 1 ether);        // full ETH taken as fee
// SwapOccurred emitted with rsETHAmount=0, fee=1 ether — no revert
``` [5](#0-4) [6](#0-5)

### Citations

**File:** contracts/pools/RSETHPoolV2NBA.sol (L106-118)
```text
    function deposit(string memory referralId) external payable nonReentrant whenNotPaused {
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
    }
```

**File:** contracts/pools/RSETHPoolV2NBA.sol (L124-133)
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

**File:** contracts/pools/RSETHPoolV2NBA.sol (L163-167)
```text
    function setFeeBps(uint256 _feeBps) external onlyRole(DEFAULT_ADMIN_ROLE) {
        if (_feeBps > 10_000) revert InvalidFeeAmount();
        feeBps = _feeBps;
        emit FeeBpsSet(_feeBps);
    }
```

**File:** contracts/L2/RsETHTokenWrapper.sol (L190-192)
```text
    function mint(address _to, uint256 _amount) external onlyRole(MINTER_ROLE) {
        _mint(_to, _amount);
    }
```
