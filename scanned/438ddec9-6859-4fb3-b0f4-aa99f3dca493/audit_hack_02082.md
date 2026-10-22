# [M] 7.2 Disabled Optimizer

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Code Corrected

The solidity optimizer has been disabled in the hardhat configuration:

```
solidity: "0.7.6",
settings: {
optimizer: {
enabled: false,
runs: 1000
}
},
```
The optimizer reduces both code size (thereby deployment costs), and execution costs.

Code corrected:

The optimizer was enabled.
