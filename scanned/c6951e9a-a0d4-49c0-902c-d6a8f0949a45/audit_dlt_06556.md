# [M] Missing Validation in addSafe Function for Enabled Guard and Module

## Summary
Severity: Medium
Chain: Smart contract
Component: Palmera
Published: 2024-06-26
Source: https://github.com/hats-finance/Palmera-0x5fee7541ddcd51ba9f4af606f87b2c42eea655be/issues/57
Type: hats-finding

## Details
**Github username:** @0xmahdirostami
**Twitter username:** 0xmahdirostami
**Submission hash (on-chain):** 0x8a527a1f843f29b2f7a4238c2a3b6e9293d5b4b1578f27446bdde2cca03e742b
**Severity:** medium

**Description:**
# Title: Missing Validation in `addSafe` Function for Enabled Guard and Module

**Description**:
The `addSafe` function currently does not validate whether the `msg.sender` has enabled the guard and the `PalmeraModule`. This oversight allows safes to be added to an organization without any guard, leading to potential security issues and possible Denial of Service (DoS) in the `disconnectSafe` and `removeWholeTree` functions.

**Impact:**
- Unauthorized safes can be added to an organization without the necessary guard.
- DoS vulnerabilities in `disconnectSafe` and `removeWholeTree` due to lack of validation.

**Proof of Concept (PoC):**

To demonstrate the issue, make the following changes in `SafeHelper.t.sol`:
```diff
function newPalmeraSafe(uint256 numberOwners, uint256 threshold)
    public
    virtual
    returns (address)
{
    require(
        privateKeyOwners.length >= numberOwners,
        "not enough initialized owners"
    );
    require(
        countUsed + numberOwners <= privateKeyOwners.length,
        "No private keys available"
    );
    require(palmeraModuleAddr != address(0), "Palmera module not set");
    address[] memory owners = new address[](numberOwners);
    for (uint256 i; i < numberOwners; ++i) {
        owners[i] = vm.addr(privateKeyOwners[i + countUsed]);
        countUsed++;
    }
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Palmera-0x5fee7541ddcd51ba9f4af606f87b2c42eea655be/issues/57_
