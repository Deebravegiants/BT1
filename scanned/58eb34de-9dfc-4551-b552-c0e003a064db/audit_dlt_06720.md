# [H] `_withdraw`  function can be called by anyone

## Summary
Severity: High
Chain: Smart contract
Component: dTRINITY
Published: 2025-06-16
Source: https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/issues/2
Type: hats-finding

## Details
**Github username:** --
  **Twitter username:** --
  **HATS Profile:** [HATS Profile](https://app.hats.finance/profile/HEX)

  **Beneficiary:** 0x92e54e1279d674fde1E65aE028A29767a9D0dbC0
  **Submission hash (on-chain):** 0x321376913e7d2e6554584f46552bbe76ac55bb16e3797562087081a44a90c4dc
  **Severity:** high
  
  **Description:**
  ## Description

The `_withdraw` function of the DStakeToken contract can be called by anyone without checking `msg.sender`, or the allowance of the same

## Attack Scenario

Simply call the `withdraw` or `redeem` functions with some `owner` that has balance and the `receiver` some address controlled by the hacker.

## Recommendation

Use the same pattern of `_withdraw` function of DPoolVaultLP contract:
```solidity
        if (caller != owner) {
            _spendAllowance(owner, caller, shares);
        }
```

## Attachments

### PoC

Add this test in `/sonic-solidity-contracts/contracts/vaults/dstake/DStakeToken.sol`:

```diff
@@ -26,6 +26,7 @@ DSTAKE_CONFIGS.forEach((config: DStakeFixtureConfig) => {
     const fixture = createDStakeFixture(config);
     let deployer: SignerWithAddress;
     let user1: SignerWithAddress;
+    let user2: SignerWithAddress;
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/issues/2_
