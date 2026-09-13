# [M] getPreviewModule() Returns Incorrect Data

## Summary
Severity: Medium
Chain: Smart contract
Component: Palmera
Published: 2024-06-30
Source: https://github.com/hats-finance/Palmera-0x5fee7541ddcd51ba9f4af606f87b2c42eea655be/issues/78
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0x7074de03867b7e8b3843e1dbfe5ce078e4c2f2b0ed6a3867f4da508818c1cda7
**Severity:** medium

**Description:**
**Description**\

`getPreviewModule()` function in the `Helpers.sol` returns the `25` modules.However, there is a bug in the external call to `safe.getModulesPaginated`. In the version of Safe contracts that Palmera is using (`version 1.3.0`), the `getPreviewModules()` function returns an incorrect next pointer, resulting in incorrect data being returned. This issue has been fixed in newer versions of Safe contracts, but Palmera still uses version `1.3.0`.


```
/// @dev Method to get Preview Module of the Safe
    /// @param safe address of the Safe
    /// @return address of the Preview Module
    function getPreviewModule(address safe) internal view returns (address) {
        // create Instance of the Safe
        ISafe safeInstance = ISafe(safe);
        // get the modules of the Safe
        (address[] memory modules, address nextModule) =
            safeInstance.getModulesPaginated(address(this), 25);

        if ((modules.length == 0) && (nextModule == Constants.SENTINEL_ADDRESS))
        {
            return Constants.SENTINEL_ADDRESS;
        } else {
            for (uint256 i = 1; i < modules.length;) {
                if (modules[i] == address(this)) {
                    return modules[i - 1];
                }
                unchecked {
                    ++i;
                }
            }
        }
    }
```

**Attack Scenario**\


**Attachments**

1. **Proof of Concept (PoC) File**
<!-- You must provide a file containing a proof of concept (PoC) that demonstrates the vulnerability you have discovered. -->
```
{
  "name": "@gnosis.pm/safe-contracts",
  "version": "1.3.0",<-----------
  "description": "Ethereum multisig contract",
  "homepage": "https://github.com/safe-global/safe-contracts/",
  "license": "GPL-3.0",
  "main": "dist/index.js",
  "typings": "dist/index.d.ts",
```

https://github.com/safe-global/safe-smart-account/blob/13c0494aca15985023b40c159c94163a4847307d/CHANGELOG.md?plain=1#L202



2. **Revised Code File (Optional)**
<!-- If possible, please provide a second file containing the revised code that offers a potential fix for the vulnerability. This file should include the following information:
- Comment with a clear explanation of the proposed fix.
- The revised code with your suggested changes.
- Any additional comments or explanations that clarify how the fix addresses the vulnerability. -->

Upgrade to a recent version of Safe.
