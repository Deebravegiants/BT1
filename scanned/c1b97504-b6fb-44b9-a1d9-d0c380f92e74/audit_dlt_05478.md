# [?] fix(sync): check height bound to avoid overflow (#1537)

## Summary
Severity: Unknown
Chain: Rollkit
Component: rollkit/rollkit
Published: 2024-03-06
Source: https://github.com/evstack/ev-node/commit/f61fa09916be6d25bc87654bf09d4d0eab847a3c
Type: security-commit

## Details
fix(sync): check height bound to avoid overflow (#1537)

## Overview

This PR adds an additional check to block height during sync. This
avoids potential integer overflow. Fixes #1455

## Checklist

- [ ] New and updated code has appropriate documentation
- [ ] New and updated code has new and/or updated testing
- [ ] Required CI checks are passing
- [ ] Visual proof for any user facing features like CLI or
documentation updates
- [ ] Linked issues closed with keywords


<!-- This is an auto-generated comment: release notes by coderabbit.ai
-->

## Summary by CodeRabbit

- **Bug Fixes**
- Added a validation check to prevent negative initial height values in
block and header synchronization processes.

<!-- end of auto-generated comment: release notes by coderabbit.ai -->
