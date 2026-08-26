# [M] Evmos allows unvested token delegations

## Summary
Severity: Medium
Chain: github.com/evmos/evmos/v18
Component: github.com/evmos/evmos/v18, github.com/evmos/evmos/v17, github.com/evmos/evmos/v16, github.com/evmos/evmos/v15, github.c
CVE: CVE-2024-37154
CWE: Improper Authorization, Incorrect Authorization
Published: 2024-06-06
Source: https://github.com/advisories/GHSA-7hrh-v6wp-53vw
Type: github-advisory

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_

At the moment, users are able to delegate tokens that have not yet been vested. This affects employees and grantees who have funds managed via `ClawbackVestingAccount`.

### Patches
_Has the problem been patched? What versions should users upgrade to?_

[The PR linked to this advisory](https://github.com/evmos/evmos-ghsa-7hrh-v6wp-53vw/pull/1) includes part of the fix. The remainder is in a [second advisory on the Cosmos SDK fork](https://github.com/evmos/cosmos-sdk/security/advisories/GHSA-wj6f-x5wv-8pqv).

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

There is no effective workaround to fix or remediate this issue without a new release. The best solution is to contain the information about this vulnerability to minimize the number of users who know about it and can thus exploit it.

### References
_Are there any links users can visit to find out more?_

See the integration tests for more details on the exploit, or use the following to reproduce it on the CLI:

1. Download `vesting_setup.json` with the following contents:
```
{
  "start_time": 1679602272,
  "periods": [
    {
      "coins": "100000000000000000000aevmos",
      "length_seconds": 10 
    },
    {
      "coins": "100000000000000000000aevmos",
      "length_seconds": 259200000
    }
  ]
}
```

2. Run the following CLI commands to reproduce the issue locally:

_Trimmed to 38 lines — full report: https://github.com/advisories/GHSA-7hrh-v6wp-53vw_
