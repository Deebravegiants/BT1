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


_Trimmed to 38 lines — full report: https://github.com/hats-finance/Palmera-0x5fee7541ddcd51ba9f4af606f87b2c42eea655be/issues/78_
