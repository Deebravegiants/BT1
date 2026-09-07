# [H] alloy-dyn-abi has DoS vulnerability on `alloy_dyn_abi::TypedData` hashing

## Summary
Severity: High
Chain: alloy-dyn-abi
Component: alloy-dyn-abi, alloy-dyn-abi
CVE: CVE-2025-62370
CWE: Improper Input Validation, Uncaught Exception
Published: 2025-10-15
Source: https://github.com/advisories/GHSA-pgp9-98jm-wwq2
Type: github-advisory

## Details
### Impact

An uncaught panic triggered by malformed input to `alloy_dyn_abi::TypedData` could lead to a denial-of-service (DoS) via `eip712_signing_hash()`.

Software with high availability requirements such as network services may be particularly impacted. If in use, external auto-restarting mechanisms can partially mitigate the availability issues unless repeated attacks are possible.

### Patches

The vulnerability was patched by adding a check to ensure the element is not empty before accessing its first element; an error is returned if it is empty. The fix is included in version [`v1.4.1`](https://crates.io/crates/alloy-dyn-abi/1.4.1) and backported to [`v0.8.26`](https://crates.io/crates/alloy-dyn-abi/0.8.26).

### Workarounds

There is no known workaround that mitigates the vulnerability. Upgrading to a patched version is the recommended course of action.

### Reported by

Christian Reitter & Zeke Mostov from [Turnkey](https://www.turnkey.com/)
