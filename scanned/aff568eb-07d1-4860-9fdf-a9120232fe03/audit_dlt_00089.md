# [H] ASA-2024-010: cosmossdk.io/math: Mismatched bit-length validation in sdk.Int and sdk.Dec can lead to panic

## Summary
Severity: High
Chain: Cosmos
Component: cosmos/cosmos-sdk
CWE: Integer Overflow or Wraparound
Published: 2024-11-20
Source: https://github.com/cosmos/cosmos-sdk/security/advisories/GHSA-7225-m954-23v7
Type: github-advisory

## Details
Name: ASA-2024-010: Mismatched bit-length in `sdk.Int` and `sdk.Dec` can lead to panic 
Component: Cosmos SDK / Math
Criticality: High (Considerable Impact, and Possible Likelihood per [ACMv1.2](https://github.com/interchainio/security/blob/main/resources/CLASSIFICATION_MATRIX.md))
Affected versions: `cosmossdk.io/math` package versions <= `math/v1.3.0`
Affected users: Chain Builders + Maintainers, Validators

### Impact

The bit-length in `sdk.Int` and `sdk.Dec` are not aligned, which may present a possible panic condition when interacting with `Dec` types in an `Int` context. This issue was resolved by aligning the max size between the data types in the cosmossdk.io/math package.

This issue impacts consumers of the cosmossdk.io/math, which includes popular modules including IBC-Go and tokenfactory (permissionless). If your chain interacts with APIs in the cosmossdk.io/math package, or utilizes a module that consumes this library, it is advised to update to the latest version at the time of the patch release by updating your project's go.mod dependency for cosmossdk.io/math.

The patch can be applied without a hard-fork, and with a version bump in a chain's go.mod file like the following:

#### `go.mod`

```diff
- cosmossdk.io/math v1.3.0
+ cosmossdk.io/math v1.4.0
```

> [!NOTE]  
> When on a lower version than cosmossdk.io/math v1.3.0, please do a coordinated upgrade before upgrading to >= 1.3.0

### Patches

The new release of `cosmossdk.io/math v1.4.0` resolves this issue.  Chains that utilize the cosmossdk.io/math library or modules that utilize the cosmossdk.io/math library should update to avoid this condition.

### Timeline

* October 31, 2024, 6:55pm UTC: Issue reported to the Cosmos Bug Bounty program
* October 31, 2024, 8:56pm UTC: Issue triaged by Amulet on-call, and distributed to Core team
* Nov 15, 2024, 2:12am PST: Core team completes patch for issue
* Nov 19, 2024, 8:00am PST / 16:00 GMT: Pre-notification delivered
* Nov 20, 2024, 8:00am PST / 16:00 GMT: Patch made available


This issue was reported by LonelySloth to the Cosmos Bug Bounty Program on HackerOne on October 31, 2024. If you believe you have found a bug in the Interchain Stack or would like to contribute to the program by reporting a bug, please see https://hackerone.com/cosmos.

_Trimmed to 38 lines — full report: https://github.com/cosmos/cosmos-sdk/security/advisories/GHSA-7225-m954-23v7_
