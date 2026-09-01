# [H] Evmos vulnerable to exploit of smart contract account and vesting

## Summary
Severity: High
Chain: github.com/evmos/evmos/v18
Component: github.com/evmos/evmos/v18
CVE: CVE-2024-39696
CWE: Incorrect Authorization
Published: 2024-07-10
Source: https://github.com/advisories/GHSA-q6hg-6m9x-5g9c
Type: github-advisory

## Details
### Summary

This advisory board aims to describe two vulnerabilities found in the Evmos codebase:

- _Authorization check on the fundVestingAccount_: unauthorized spend of funds.

### Details

#### Authorization check on the fundVestingAccount

With the current implementation, a user can create a vesting account with a 3rd party account (EOA or contract) as funder. Then, this user can create an authorization for the contract.CallerAddress, this is the authorization checked in the code. But the funds are taken from the funder address provided in the message. Consequently, the user can fund a vesting account with a 3rd party account without its permission. The funder address can be any address, so this vulnerability can be used to drain all the accounts in the chain.

### Severity
Based on [ImmuneFi Severity Classification System](https://immunefisupport.zendesk.com/hc/en-us/articles/13332717597585-Severity-Classification-System) the severity was evaluated to Critical since the attack could have lead to direct loss of funds.

### Patches
The issue has been patched in versions >=V19.0.0
