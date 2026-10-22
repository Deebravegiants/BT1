# [M] 5.1 Race Condition on Approvals

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Risk Accepted

Since there is no direct way to increase and decrease allowance relative to its current value, the function
AllowanceTransfer.approve() has a race condition similar to one of ERC-20 approvals. Further
details regarding the race condition can be found here.

Risk accepted:

Uniswap responded:

```
We opted not to address this issue. If users really care about this attack vector it
means they are likely signing a spender they don’t fully trust, and they can always approve(x),
approve(0), approve(y). We also expose a lockdown function that can batch remove approvals for users,
before setting new approvals.
```


Here, we list findings that have been resolved during the course of the engagement. Their categories are
explained in the Findings section.

Below we provide a numerical overview of the identified findings, split up by their severity.

```
Critical-Severity Findings 0
```
```
High-Severity Findings 1
```
- Permit2Lib Argument Casting Code Corrected

```
Medium-Severity Findings 0
```
```
Low-Severity Findings 1
```
- CALL to DOMAIN_SEPARATOR() Code Corrected
