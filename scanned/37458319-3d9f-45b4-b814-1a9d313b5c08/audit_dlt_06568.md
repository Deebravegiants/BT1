# [M] Any contract can bypass `isSafe` restrictions

## Summary
Severity: Medium
Chain: Smart contract
Component: Palmera
Published: 2024-06-24
Source: https://github.com/hats-finance/Palmera-0x5fee7541ddcd51ba9f4af606f87b2c42eea655be/issues/24
Type: hats-finding

## Details
**Github username:** @0xfuje
**Twitter username:** 0xfuje
**Submission hash (on-chain):** 0xe58592223e20a1148ea47089a11616fe4ccd1063acef32e9956bf64700de509a
**Severity:** medium

**Description:**
## Description
User can create a non-safe custom contract that returns `1` on `getThreshold()` calls to use `PalmeraModule` functionality.

Non-safe contracts can registers organization, create a root safe, and be added as a safe in `addSafe()`, basically bypass the `isSafe()` restrictions.


 `src/Helpers.sol` - `isSafe()`
 ```solidity
     function isSafe(address safe) public view returns (bool) { // @audit m - any contract can bypass isSafe calls
        /// Check if the address is a Safe Smart Account Wallet
        if (safe.isContract()) {
            /// Check if the address is a Safe Multisig Wallet
            bytes memory payload = abi.encodeCall(ISafe.getThreshold, ());
            (bool success, bytes memory returnData) = safe.staticcall(payload);
            if (!success) return false;
            /// Check if the address is a Safe Smart Account Wallet
            uint256 threshold = abi.decode(returnData, (uint256));
            if (threshold == 0) return false;
            return true;
        } else {
            return false;
        }
    }
 ```

## Recommendation
Consider to implement stricter checks, for example: `ERC165` `supportsInterface()` checks instead of only checking `safe` is a contract and `threshold` in `isSafe()`.
