# [?] github: Remove vulnerability.md (#21894)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2020-11-24
Source: https://github.com/ethereum/go-ethereum/commit/7e7a3f0f71d60510afb5cd06282c1db729c1f60b
Type: security-commit

## Details
github: Remove vulnerability.md (#21894)

This type is automatically offered by github after changing to the new style and a security.md being present

## Patch
### .github/ISSUE_TEMPLATE/vulnerability.md
```diff
@@ -1,13 +0,0 @@
----
-name: Report a vulnerability
-about: There is a bug in go-ethereum that can be exploited
-title: ''
-labels: 'type:security'
-assignees: ''
----
-
-Please do not submit these in this public issue tracker!
-
-To find out how to disclose a vulnerability in Ethereum visit https://bounty.ethereum.org or email bounty@ethereum.org.
-
-Please read [Reporting a vulnerability](https://github.com/ethereum/go-ethereum/security/policy#reporting-a-vulnerability) for more information.
```
