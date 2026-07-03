### Title
Single-step `setCustodyAddress` Update Enables Permanent Loss of User rsETH via `recoverFrozenFunds` - (File: contracts/RSETH.sol)

### Summary
`RSETH.sol` exposes a two-function combination that mirrors the CSX Council vulnerability exactly: `setCustodyAddress` updates the destination for forcibly drained user rsETH in a single atomic step with no confirmation, while `recoverFrozenFunds` can drain a blocked user's entire rsETH balance to that address. If the admin accidentally sets `custodyAddress` to a wrong address, the next `recoverFrozenFunds` call permanently transfers user funds to an unintended destination with no recovery path.

### Finding Description
`RSETH.sol` contains a fund-recovery mechanism composed of two privileged functions:

**`setCustodyAddress`** — updates `custodyAddress` in a single step with no two-step confirmation or timelock:

```solidity
function setCustodyAddress(address newCustodyAddress) external onlyLRTAdmin {
    _setCustodyAddress(newCustodyAddress);
}

function _setCustodyAddress(address newCustodyAddress) internal {
    UtilLib.checkNonZeroAddress(newCustodyAddress);
    custodyAddress = newCustodyAddress;
    emit CustodyAddressUpdated(newCustodyAddress);
}
```

**`recoverFrozenFunds`** — forcibly transfers the entire rsETH balance of a currently-blocked user to `custodyAddress`, bypassing the normal transfer-block enforcement:

```solidity
function recoverFrozenFunds(address from) external onlyLRTAdmin {
    ...
    uint256 accountBalance = balanceOf(from);
    // Bypass transfer block enforcement when transferring to custody address
    super._transfer(from, custodyAddress, accountBalance);
    emit FrozenFundsRecovered(from, custodyAddress, accountBalance);
}
```

The `onlyLRTAdmin` modifier resolves to `DEFAULT_ADMIN_ROLE` in `LRTConfig` via `LRTConfigRoleChecker`. There is no pending-address queue, no acceptance step, and no delay between setting `custodyAddress` and it taking effect for the next `recoverFrozenFunds` call.

The structural parallel to the CSX report is direct:

| CSX | LRT-rsETH |
|---|---|
| `changeCouncil(addr)` — single-step Council role transfer | `setCustodyAddress(addr)` — single-step custody destination update |
| `cliff()` — forced drain of user tokens to Council address | `recoverFrozenFunds(from)` — forced drain of user rsETH to `custodyAddress` |
| Wrong Council address receives drained tokens | Wrong `custodyAddress` receives drained rsETH |

### Impact Explanation
If the admin sets `custodyAddress` to an incorrect address (e.g., a dead address, a contract that cannot receive ERC-20 tokens, or an address controlled by an unintended party), the next invocation of `recoverFrozenFunds` on any blocked user permanently transfers that user's entire rsETH balance to the wrong destination. The `super._transfer` call bypasses the transfer-block check, so the transfer executes unconditionally. There is no on-chain mechanism to reverse it. This constitutes direct, permanent theft or freezing of user funds.

**Impact: Critical — Direct theft / permanent freezing of user rsETH.**

### Likelihood Explanation
The LRT Manager can block any non-exempt user's transfers at any time via `blockUserTransfers`. The admin is expected to call `setCustodyAddress` before or during compliance-related fund recovery operations. A single address typo, copy-paste error, or use of a staging address in production is sufficient to misdirect all subsequent `recoverFrozenFunds` calls. The absence of a two-step confirmation removes the only natural error-correction checkpoint. Likelihood is **Low** but the consequence is irreversible.

### Recommendation
1. Implement a two-step process for `setCustodyAddress`: the admin nominates a new address, and the nominated address must call an `acceptCustodyRole()` function to confirm it is live and controlled. This mirrors the fix recommended in the CSX report.
2. Alternatively, gate `setCustodyAddress` behind a `TimelockController` so that any change is subject to a mandatory delay, giving operators time to detect and cancel an erroneous update before it is used in a `recoverFrozenFunds` call.

### Proof of Concept
```
1. LRT Manager calls blockUserTransfers([victim])
   → victim's transfers are blocked for 24 hours

2. LRT Admin calls setCustodyAddress(wrongAddress)
   → wrongAddress is a typo / dead address / attacker-controlled address
   → no confirmation required; custodyAddress is immediately updated

3. LRT Admin calls recoverFrozenFunds(victim)
   → super._transfer(victim, wrongAddress, victim.rsETHBalance) executes
   → victim's entire rsETH balance is permanently sent to wrongAddress
   → no on-chain recovery path exists
```

**Relevant code locations:** [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** contracts/RSETH.sol (L199-201)
```text
    function setCustodyAddress(address newCustodyAddress) external onlyLRTAdmin {
        _setCustodyAddress(newCustodyAddress);
    }
```

**File:** contracts/RSETH.sol (L206-220)
```text
    function recoverFrozenFunds(address from) external onlyLRTAdmin {
        UtilLib.checkNonZeroAddress(from);
        UtilLib.checkNonZeroAddress(custodyAddress);

        if (isPermanentlyExempt[from]) revert AddressPermanentlyExempt(from);

        uint256 blockedUntil = transfersBlockedUntil[from];
        if (blockedUntil == 0 || block.timestamp >= blockedUntil) revert NoActiveTransferBlock(from);

        uint256 accountBalance = balanceOf(from);

        // Bypass transfer block enforcement when transferring to custody address
        super._transfer(from, custodyAddress, accountBalance);
        emit FrozenFundsRecovered(from, custodyAddress, accountBalance);
    }
```

**File:** contracts/RSETH.sol (L309-313)
```text
    function _setCustodyAddress(address newCustodyAddress) internal {
        UtilLib.checkNonZeroAddress(newCustodyAddress);
        custodyAddress = newCustodyAddress;
        emit CustodyAddressUpdated(newCustodyAddress);
    }
```

**File:** contracts/utils/LRTConfigRoleChecker.sol (L58-63)
```text
    modifier onlyLRTAdmin() {
        if (!IAccessControl(address(lrtConfig)).hasRole(LRTConstants.DEFAULT_ADMIN_ROLE, msg.sender)) {
            revert ILRTConfig.CallerNotLRTConfigAdmin();
        }
        _;
    }
```
