### Title
Daily Mint Limit Exhaustion via Unrestricted Micro-Deposits Enabling Block Stuffing Griefing - (File: contracts/pools/RSETHPoolV3ExternalBridge.sol)

### Summary

The `deposit(string)` and `deposit(address,uint256,string)` functions in `RSETHPoolV3ExternalBridge` impose no minimum deposit size beyond `amount > 0`. The `limitDailyMint` modifier tracks cumulative `dailyMintAmount` against `dailyMintLimit` with no per-transaction floor. On cheap L2s (Base, Linea), an attacker can submit many tiny deposits — each consuming a negligible fraction of the daily limit — at near-zero gas cost, exhausting `dailyMintLimit` within a single block window and locking out all other depositors for the remainder of the 24-hour period.

### Finding Description

The `limitDailyMint` modifier: [1](#0-0) 

computes `rsETHAmount` from the raw deposit `amount` and checks:

```solidity
if (dailyMintAmount + rsETHAmount > dailyMintLimit) revert DailyMintLimitExceeded();
dailyMintAmount += rsETHAmount;
```

There is no lower bound on `rsETHAmount` per call. The ETH deposit path: [2](#0-1) 

only rejects `amount == 0`: [3](#0-2) 

An attacker can therefore send `N` transactions each depositing `dailyMintLimit / N` worth of ETH (or 1 wei each, accumulating rounding dust). Because the attacker **receives wrsETH back**, their net economic cost is only gas. On Base/Linea, gas per transaction is a fraction of a cent, making it trivial to send thousands of transactions that collectively exhaust `dailyMintLimit`.

The block stuffing dimension: the attacker broadcasts all `N` transactions with a gas price high enough to fill the block gas limit, preventing legitimate user transactions from being included in those same blocks. By the time legitimate transactions land, `dailyMintAmount >= dailyMintLimit` and every subsequent deposit reverts with `DailyMintLimitExceeded` until the next UTC day boundary computed by: [4](#0-3) 

### Impact Explanation

Temporary freezing of user deposit access for up to 24 hours. All legitimate depositors are denied access to the pool for the remainder of the day window. The attacker suffers no capital loss (they hold wrsETH equivalent to their ETH input) and pays only L2 gas, which on Base/Linea is negligible relative to the value of deposits blocked.

### Likelihood Explanation

The attack is permissionless, requires no privileged role, no oracle manipulation, and no external protocol compromise. The only prerequisite is sufficient ETH to fill the daily limit (which the attacker recovers as wrsETH) and cheap L2 gas. The absence of any minimum deposit guard — unlike, for example, `KernelVaultETH` which enforces `minDeposit`: [5](#0-4) 

— makes this straightforwardly exploitable.

### Recommendation

Enforce a minimum deposit amount in `RSETHPoolV3ExternalBridge` analogous to the `minDeposit` pattern already used in `KernelVaultETH`. Add an admin-configurable `minDepositAmount` state variable and check it at the top of both `deposit` overloads:

```solidity
if (amount < minDepositAmount) revert DepositAmountTooLow();
```

This raises the per-transaction cost for limit exhaustion proportionally, making the attack economically infeasible.

### Proof of Concept

```solidity
// Fork test on Base/Linea
function testBlockStuffingLimitExhaustion() external {
    uint256 dailyLimit = pool.dailyMintLimit(); // e.g. 100 ether in rsETH
    uint256 N = 10_000;
    uint256 depositPerTx = dailyLimit / N; // tiny ETH per tx

    // Attacker sends N deposits, each consuming dailyLimit/N of the cap
    for (uint256 i = 0; i < N; i++) {
        vm.prank(attacker);
        pool.deposit{value: depositPerTx}("ref");
    }

    // Legitimate user deposit now reverts
    vm.prank(victim);
    vm.expectRevert(RSETHPoolV3ExternalBridge.DailyMintLimitExceeded.selector);
    pool.deposit{value: 1 ether}("ref");

    // Attacker holds wrsETH ≈ dailyLimit; net ETH cost = 0 (recovered as wrsETH)
    // Attacker gas cost on Base ≈ N * ~0.0001 USD = ~$1 total
}
```

### Citations

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L130-158)
```text
    modifier limitDailyMint(uint256 amount, address token) {
        if (block.timestamp < startTimestamp) {
            revert MintBeforeStartTimestamp();
        }

        uint256 rsETHAmount;

        // Calculate the amount of rsETH that will be minted
        if (token == ETH_IDENTIFIER) {
            (rsETHAmount,) = viewSwapRsETHAmountAndFee(amount);
        } else {
            (rsETHAmount,) = viewSwapRsETHAmountAndFee(amount, token);
        }

        uint256 currentDay = getCurrentDay();

        // If the current day is greater than the last mint day, reset the daily mint amount
        if (currentDay > lastMintDay) {
            lastMintDay = currentDay;
            dailyMintAmount = 0;
        }

        // Check if the daily mint amount plus the amount to mint is greater than the daily mint limit
        if (dailyMintAmount + rsETHAmount > dailyMintLimit) {
            revert DailyMintLimitExceeded();
        }

        dailyMintAmount += rsETHAmount;
        _;
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L366-384)
```text
    function deposit(string memory referralId)
        external
        payable
        nonReentrant
        whenNotPaused
        limitDailyMint(msg.value, ETH_IDENTIFIER)
    {
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
    }
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L548-549)
```text
    function getCurrentDay() public view returns (uint256) {
        return (block.timestamp - startTimestamp) / 1 days;
```

**File:** contracts/KERNEL/KernelVaultETH.sol (L385-387)
```text
        if (amount < minDeposit) {
            revert DepositAmountTooLow();
        }
```
