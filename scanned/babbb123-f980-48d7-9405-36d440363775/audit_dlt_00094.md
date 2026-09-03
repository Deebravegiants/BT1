# [M] Barberry Security Advisory - regarding x/auth periodic vesting accounts

## Summary
Severity: Medium
Chain: Cosmos
Component: cosmos/cosmos-sdk
Published: 2023-07-07
Source: https://github.com/cosmos/cosmos-sdk/security/advisories/GHSA-j2cr-jc39-wpx5
Type: github-advisory

## Details
### Impact

In `PeriodicVestingAccount`, defined in `x/auth`, an attacker can initialize a victim's account as a malicious vesting account, which allows deposits but does not allow withdrawals. When the user then deposits funds into their account, those funds are locked forever, and the user is not able to withdraw them.

### Patches

\>= v0.46.13 for Cosmos SDK v0.46.x
\>= v0.47.3 for Cosmos SDK v0.47.x

If a network backported periodic vesting accounts to earlier versions of the SDK, those networks are affected too.

### Workarounds

There is no workaround for this issue. Upgrade immediately.

### References

* Patched versions release notes: [v0.47.3](https://github.com/cosmos/cosmos-sdk/blob/cfc757dc5043fb2758c47c146d2912fd010c1a45/RELEASE_NOTES.md#cosmos-sdk-v0473-release-notes), [v0.46.13](https://github.com/cosmos/cosmos-sdk/blob/d4b7164de5d8391e6aa644d8ea84e07396dd9653/RELEASE_NOTES.md#cosmos-sdk-v04613-release-notes).
* [Forum Post](https://forum.cosmos.network/t/cosmos-sdk-security-advisory-barberry/10825)
