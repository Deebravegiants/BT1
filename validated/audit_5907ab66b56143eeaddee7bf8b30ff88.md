### Title
Manager Can Accidentally Donate Own ETH to Protocol via Unnecessarily `payable` Deposit Function - (File: contracts/L1Vault.sol, contracts/L1VaultV2.sol)

### Summary
`L1Vault.depositETHForL1VaultETH()` and `L1VaultV2.depositETHForL1VaultETH()` are declared `payable` but compute the deposit amount from `address(this).balance` rather than `msg.value`. Any ETH the manager accidentally attaches to the call is silently swept into the deposit, minting rsETH to the vault (not the manager), and the manager's ETH is permanently lost.

### Finding Description
Both `L1Vault` and `L1VaultV2` implement `depositETHForL1VaultETH` as follows:

```solidity
function depositETHForL1VaultETH() external payable nonReentrant onlyRole(MANAGER_ROLE) {
    uint256 balanceOfETH = address(this).balance;          // includes msg.value
    uint256 rsETHAmountToMint = lrtDepositPool.getRsETHAmountToMint(ETH_IDENTIFIER, balanceOfETH);
    if (rsETHAmountToMint == 0) revert InvalidMinRSETHAmountExpected();
    lrtDepositPool.depositETH{ value: balanceOfETH }(rsETHAmountToMint, "");
    emit ETHDepositForL1Vault(balanceOfETH, rsETHAmountToMint);
}
```

The function's purpose is to deposit ETH that was already bridged from L2 and is sitting in the vault. There is no legitimate reason for the manager to attach ETH to this call. However, because the function is `payable`, any ETH sent via `msg.value` is silently included in `address(this).balance` and forwarded to `lrtDepositPool.depositETH`. The rsETH is minted to `address(this)` (the vault), not to the manager. The manager's ETH is permanently absorbed into the protocol.

This is the direct analog of the M-01 pattern: a function is `payable` when it should not be, allowing the wrong party to accidentally fund a transaction intended to be funded by a different source (the bridged ETH already in the vault).

### Impact Explanation
A manager who accidentally attaches ETH to the `depositETHForL1VaultETH` call loses that ETH permanently. The ETH is deposited into `LRTDepositPool`, rsETH is minted to the L1Vault, and the vault subsequently bridges that rsETH to L2 users. The manager receives nothing in return for their ETH. This constitutes a permanent, irrecoverable loss of the manager's own funds.

**Impact: Low** — Contract fails to deliver promised returns to the manager (their ETH is consumed without compensation), but the protocol itself does not lose value.

### Likelihood Explanation
The manager must call `depositETHForL1VaultETH()` and accidentally include a non-zero `msg.value`. This is a realistic operational mistake (e.g., copy-pasting a transaction template that included ETH, or a scripting error). The function provides no warning or revert when `msg.value > 0`, making the mistake silent and undetectable until after the fact.

**Likelihood: Low** — Requires a specific operational mistake by the manager, but the silent acceptance of ETH makes it easy to miss.

### Recommendation
Remove the `payable` modifier from `depositETHForL1VaultETH()` in both `L1Vault` and `L1VaultV2`. The function has no legitimate use for `msg.value`; all ETH to be deposited should already reside in the vault from the L2 bridge. Alternatively, add an explicit check:

```solidity
if (msg.value != 0) revert UnexpectedETH();
```

### Proof of Concept
1. ETH is bridged from L2 to `L1Vault` via the native bridge; vault holds 10 ETH.
2. Manager prepares a call to `depositETHForL1VaultETH()` but accidentally attaches 1 ETH (e.g., scripting error).
3. `address(this).balance` = 11 ETH (10 bridged + 1 manager's).
4. `lrtDepositPool.depositETH{ value: 11 ETH }(...)` is called; rsETH for 11 ETH is minted to the L1Vault.
5. Manager's 1 ETH is permanently lost; they receive no rsETH or refund. [1](#0-0) [2](#0-1)

### Citations

**File:** contracts/L1Vault.sol (L150-161)
```text
    function depositETHForL1VaultETH() external payable nonReentrant onlyRole(MANAGER_ROLE) {
        uint256 balanceOfETH = address(this).balance;
        uint256 rsETHAmountToMint = lrtDepositPool.getRsETHAmountToMint(ETH_IDENTIFIER, balanceOfETH);

        if (rsETHAmountToMint == 0) {
            revert InvalidMinRSETHAmountExpected();
        }

        lrtDepositPool.depositETH{ value: balanceOfETH }(rsETHAmountToMint, "");

        emit ETHDepositForL1Vault(balanceOfETH, rsETHAmountToMint);
    }
```

**File:** contracts/L1VaultV2.sol (L224-235)
```text
    function depositETHForL1VaultETH() external payable nonReentrant onlyRole(MANAGER_ROLE) {
        uint256 balanceOfETH = address(this).balance;
        uint256 rsETHAmountToMint = lrtDepositPool.getRsETHAmountToMint(ETH_IDENTIFIER, balanceOfETH);

        if (rsETHAmountToMint == 0) {
            revert InvalidMinRSETHAmountExpected();
        }

        lrtDepositPool.depositETH{ value: balanceOfETH }(rsETHAmountToMint, "");

        emit ETHDepositForL1Vault(balanceOfETH, rsETHAmountToMint);
    }
```
