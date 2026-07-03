### Title
Token Deposits in RSETHPool Always Pay Zero Fee Due to Uninitialized `tokenFeeBps` - (File: contracts/pools/RSETHPool.sol)

### Summary

`RSETHPool.addSupportedToken` never initializes `tokenFeeBps[token]`, which defaults to `0`. Every call to `deposit(token, amount, referralId)` therefore computes a fee of zero for all ERC-20 token deposits, permanently bypassing protocol fee collection on that path.

### Finding Description

`RSETHPool` maintains two separate fee variables: `feeBps` (used for ETH deposits) and a per-token mapping `tokenFeeBps[token]` (used for ERC-20 token deposits).

When a new token is added via `addSupportedToken`, only `supportedTokenOracle[token]` and `tokenBridge[token]` are written. `tokenFeeBps[token]` is never set and therefore retains the Solidity default of `0`. [1](#0-0) 

The fee computation for token deposits reads directly from this uninitialized mapping:

```solidity
uint256 feeBpsForToken = tokenFeeBps[token];
fee = amount * feeBpsForToken / 10_000;   // always 0
``` [2](#0-1) 

Because `fee = 0`, the full `amount` is used as `amountAfterFee`, and `feeEarnedInToken[token]` is incremented by zero. No fee is ever collected for any token deposit. [3](#0-2) 

The ETH deposit path is unaffected because it uses the separate `feeBps` variable, which is properly initialized. [4](#0-3) 

### Impact Explanation

**High — Theft of unclaimed yield.** The protocol is designed to collect swap fees on token deposits and accumulate them in `feeEarnedInToken[token]` for later withdrawal by the `BRIDGER_ROLE`. Because `tokenFeeBps[token]` is always `0`, every token depositor receives the full rsETH equivalent of their deposit with no fee deducted. All protocol fee revenue from the token deposit path is permanently lost until an admin explicitly calls `setTokenFeeBps`. Any volume processed before that call generates zero fee income for the protocol.

### Likelihood Explanation

**High.** The condition is triggered automatically for every supported ERC-20 token from the moment it is added. No special attacker setup is required — any ordinary depositor calling `deposit(token, amount, referralId)` exploits the zero-fee path. The only mitigation is an out-of-band admin call to `setTokenFeeBps`, which is not enforced or documented as a required post-`addSupportedToken` step.

### Recommendation

Initialize `tokenFeeBps[token]` inside `addSupportedToken`, either to the global `feeBps` value or to an explicit parameter supplied by the caller:

```solidity
function addSupportedToken(
    address token,
    address oracle,
    address bridge,
    uint256 _feeBps          // <-- add this parameter
) external onlyRole(TIMELOCK_ROLE) {
    ...
    tokenFeeBps[token] = _feeBps;
    ...
}
```

Alternatively, fall back to `feeBps` when `tokenFeeBps[token]` is zero, mirroring the intent of the global fee setting.

### Proof of Concept

1. Admin calls `addSupportedToken(wstETH, oracle, bridge)` — `tokenFeeBps[wstETH]` is never written, remains `0`.
2. User calls `deposit(wstETH, 10 ether, "")`.
3. `viewSwapRsETHAmountAndFee(10 ether, wstETH)` executes:
   - `feeBpsForToken = tokenFeeBps[wstETH]` → `0`
   - `fee = 10 ether * 0 / 10_000` → `0`
   - `amountAfterFee = 10 ether`
4. User receives rsETH equivalent of the full `10 ether` with no fee deducted.
5. `feeEarnedInToken[wstETH] += 0` — protocol collects nothing.

Compare with the ETH deposit path where `feeBps` (e.g., 5 bps) is always applied:
- `fee = 10 ether * 5 / 10_000` → `0.005 ether` collected.

The discrepancy means the entire token deposit volume generates zero protocol revenue, directly analogous to the Putty Finance finding where zero-strike calls produced a zero fee because the fee was computed as `strike * feeBps / 1000` and `strike = 0`. [5](#0-4) [6](#0-5)

### Citations

**File:** contracts/pools/RSETHPool.sol (L88-89)
```text
    mapping(address token => uint256 feeBps) public tokenFeeBps;

```

**File:** contracts/pools/RSETHPool.sol (L284-305)
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
    {
        if (amount == 0) revert InvalidAmount();

        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        IERC20(address(wrsETH)).safeTransfer(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId); // Add token address?
    }
```

**File:** contracts/pools/RSETHPool.sol (L311-313)
```text
    function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;
```

**File:** contracts/pools/RSETHPool.sol (L335-337)
```text
        uint256 feeBpsForToken = tokenFeeBps[token];
        fee = amount * feeBpsForToken / 10_000;
        uint256 amountAfterFee = amount - fee;
```

**File:** contracts/pools/RSETHPool.sol (L583-594)
```text
    function setTokenFeeBps(
        address token,
        uint256 _feeBps
    )
        external
        onlyRole(DEFAULT_ADMIN_ROLE)
        onlySupportedToken(token)
    {
        if (_feeBps > 10_000) revert InvalidFeeAmount();
        tokenFeeBps[token] = _feeBps;
        emit TokenFeeBpsSet(token, _feeBps);
    }
```

**File:** contracts/pools/RSETHPool.sol (L637-656)
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
    }
```
