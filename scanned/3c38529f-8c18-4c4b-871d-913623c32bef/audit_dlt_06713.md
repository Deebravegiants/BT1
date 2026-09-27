# [H] Invariant Violation Due to Unchecked Deallocation from Inactive or Unallocated AMO Vaults

## Summary
Severity: High
Chain: Smart contract
Component: dTRINITY
Published: 2025-06-16
Source: https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/issues/42
Type: hats-finding

## Details
**Github username:** --
  **Twitter username:** --
  **HATS Profile:** [HATS Profile](https://app.hats.finance/profile/dod4ufn)

  **Beneficiary:** 0xf8e45a12a45CfBa70a24c00BC3492Ab948f028EE
  **Submission hash (on-chain):** 0xe6cbb8337de1ff47aa69e5a8a03b0d2bada323e768d0c2f52da99d8b818afe7a
  **Severity:** high
  
  **Description:**
  **Description**
The `deallocateAmo` function allows deallocation of `dstableAmount` from any AMO vault, including inactive ones or those with zero current allocation. This permissive logic introduces a critical vulnerability: it allows reducing the global `totalAllocated` counter without guaranteeing that the vault being deallocated from had previously increased this counter via `allocateAmo`.

As a result, if deallocation occurs on a vault that was either never allocated or is currently inactive (with zero or insufficient allocation), `totalAllocated` is reduced incorrectly. This leads to a situation where `totalAllocated` becomes less than the sum of actual vault allocations, breaking the expected accounting invariants. Future calls to `deallocateAmo` for other (properly allocated) vaults may then revert due to insufficient `totalAllocated`, even though the underlying vaults still hold funds and valid allocations.

---

**Attack Scenario**

1. The function `deallocateAmo(vault, amount)` is called on a vault with 0 current allocation.
2. The function skips any allocation checks and unconditionally reduces `totalAllocated` by `amount`.
3. Since the vault had no allocation, this results in an underflow of accounting logic (though not an actual underflow), breaking consistency.
4. When a legitimate vault later attempts to deallocate its properly allocated funds, the contract may revert due to `totalAllocated` being insufficient, even though the vault holds valid assets.

This can lead to DoS conditions for other AMO vaults.

---

**Recommendation**

Either prohibit deallocating from `_amoVaults` with 0 allocation, or do not subtract the `dstableAmount` from `totalAllocated` when the `_amoVault` has 0 allocation.
