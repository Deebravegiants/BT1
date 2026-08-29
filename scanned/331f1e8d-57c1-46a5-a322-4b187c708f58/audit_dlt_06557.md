# [H] Potential Protocol insolvency in `removeWholeTree` and `disconnectSafe`

## Summary
Severity: High
Chain: Smart contract
Component: Palmera
Published: 2024-06-25
Source: https://github.com/hats-finance/Palmera-0x5fee7541ddcd51ba9f4af606f87b2c42eea655be/issues/55
Type: hats-finding

## Details
**Github username:** @0xmahdirostami
**Twitter username:** 0xmahdirostami
**Submission hash (on-chain):** 0xd77a9b46593e4a7658ab290f9fe2d76a34d5ed7ef1b4e5558a5f286e8c6d8cf2
**Severity:** high

**Description:**
**Description**:
The `_exitSafe` function currently includes a check for `getPreviewModule(caller)` and reverts if it returns `address(0)`. This can lead to a Denial of Service (DoS) issue because users can call `disableModule` on their own, causing subsequent calls to `_exitSafe` to fail.

**Impact:**
The DoS vulnerability in `_exitSafe` affects the `removeWholeTree` and `disconnectSafe` functions. If `disableModule` has been called by the user, it will result in a failure of `_exitSafe`, thereby preventing the proper execution of these functions, leading to Protocol insolvency.

**Proof of Concept (PoC):**

Here is the relevant code snippet in `_exitSafe`:
```solidity
function _exitSafe(address caller) internal {
    // Some other code...

    address prevModule = getPreviewModule(caller);
    if (prevModule == address(0)) {
        revert Errors.PreviewModuleNotFound(_safe);
    }
    data = abi.encodeCall(ISafe.disableModule, (prevModule, address(this)));
    // Execute transaction from target safe
    _executeModuleTransaction(_safe, data);

    emit Events.SafeDisconnected(org, safeId, address(safeTarget), caller);
}
```

If a user has previously called `disableModule`, `getPreviewModule(caller)` will return `address(0)`, leading to the function reverting.

**Suggested Test Case:**

please change the following:
```diff
-    function getPreviewModule(address safe) internal view returns (address) {
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Palmera-0x5fee7541ddcd51ba9f4af606f87b2c42eea655be/issues/55_
