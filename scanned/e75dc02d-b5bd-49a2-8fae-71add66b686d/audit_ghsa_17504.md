# [M] pycares has a Use-After-Free Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-5qpg-rh4j-qp35
CWE: CWE-416
Ecosystem: PyPI
Published: 2025-06-16
Source: https://github.com/advisories/GHSA-5qpg-rh4j-qp35
Type: github-advisory

## Affected
- PyPI: `pycares` — affected >=0 <4.9.0

## Details
## Summary

pycares is vulnerable to a use-after-free condition that occurs when a Channel object is garbage collected while DNS queries are still pending. This results in a fatal Python error and interpreter crash.

## Details

### Root Cause

The vulnerability stems from improper handling of callback references when the Channel object is destroyed:

1. When a DNS query is initiated, pycares stores a callback reference using `ffi.new_handle()`
2. If the Channel object is garbage collected while queries are pending, the callback references become invalid
3. When c-ares attempts to invoke the callback, it accesses freed memory, causing a fatal error

This issue was much more likely to occur when using `event_thread=True` but could happen without it under the right circumstances.

### Technical Details

The core issue is a race condition between Python's garbage collector and c-ares's callback execution:

1. When `__del__` is called from within a c-ares callback context, we cannot immediately call `ares_destroy()` because c-ares is still executing code after the callback returns
2. c-ares needs to execute cleanup code after our Python callback returns (specifically at lines 1422-1429 in ares_process.c)
3. If we destroy the channel too quickly, c-ares accesses freed memory

### Impact

Applications using `pycares` can be crashed remotely by triggering DNS queries that result in `Channel` objects being garbage collected before query completion. This is particularly problematic in scenarios where:

- Channel objects are created per-request
- Multiple failed DNS queries are processed rapidly
- The application doesn't properly manage Channel lifecycle

The error manifests as:
```
Fatal Python error: b_from_handle: ffi.from_handle() detected that the address passed points to garbage
```

## Fix

The vulnerability has been fixed in pycares 4.9.0 by implementing a safe channel destruction mechanism

## Mitigation

### For Application Developers

1. **Upgrade to pycares >= 4.9.0** - This version includes the fix and requires no code changes
2. **Best practices** (optional but recommended):
   ```python
   # Explicit cleanup
   channel.close()
   
   # Or use context manager
   with pycares.Channel() as channel:
       # ... use channel ...
   # Automatically closed
   ```
3. **Avoid creating Channel objects per-request** - Prefer long-lived instances for better performance and safety

The fix is completely transparent - no API changes or code modifications are required.

## Credit

This vulnerability was reported by @vEpiphyte through the aio-libs security program.

## References
- https://github.com/saghul/pycares/security/advisories/GHSA-5qpg-rh4j-qp35
- https://github.com/saghul/pycares/commit/ebfd7d71eb8e74bc1057a361ea79a5906db510d4
- https://github.com/saghul/pycares
