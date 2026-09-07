# [M] Missing `disableSafeLeadRoles` Call for Root in `removeWholeTree` Function**

## Summary
Severity: Medium
Chain: Smart contract
Component: Palmera
Published: 2024-06-28
Source: https://github.com/hats-finance/Palmera-0x5fee7541ddcd51ba9f4af606f87b2c42eea655be/issues/72
Type: hats-finding

## Details
**Github username:** @0xmahdirostami
**Twitter username:** 0xmahdirostami
**Submission hash (on-chain):** 0xaad7afa14366c6b8c37347f008d96027c424ac49bfd1b2a4529532c1c739661f
**Severity:** medium

**Description:**
**Description:**

In the `removeWholeTree` function, the `disableSafeLeadRoles` function is not called for the root safe. The relevant code snippet is:

```solidity
            disableSafeLeadRoles(safes[org][safe].safe);
            _exitSafe(safe);
            unchecked {
                ++j;
            }
        }
        // After Disconnect Root Safe
        _exitSafe(rootSafe);
```

This snippet shows that `disableSafeLeadRoles` is called for all safes but not for the root safe.

**Impact:**
- The lack of disabling lead roles for the root will cause issues, especially if the root safe becomes a member in another organization. This can result in unexpected behavior and potential security risks, as the root safe will retain roles that should have been disabled.

**Mitigation:**

To mitigate this issue, ensure that `disableSafeLeadRoles` is also called for the root safe. The corrected code should look like this:

```diff
            disableSafeLeadRoles(safes[org][safe].safe);
            _exitSafe(safe);
            unchecked {
                ++j;
            }
        }
        // After Disconnect Root Safe
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Palmera-0x5fee7541ddcd51ba9f4af606f87b2c42eea655be/issues/72_
