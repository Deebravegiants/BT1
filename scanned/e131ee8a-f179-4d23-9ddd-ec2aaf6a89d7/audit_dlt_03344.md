# [H] Users are charged twice the FDT tokens when tokenizing their convictions

## Summary
Severity: High
Chain: Smart contract
Component: 2021-05-fairside
Published: 2021-05-27
Source: https://github.com/code-423n4/2021-05-fairside-findings/issues/74
Type: code-finding

## Details
# Handle

shw


# Vulnerability details

## Impact

Users have to pay twice the FSD tokens when tokenizing their convictions if the `locked` variable is non-zero.

## Proof of Concept

The first payment is made in the function `tokenizeConviction` of the contract `ERC20ConvictionScore` (line 282), where a user transfer `locked` amount of FSD to the contract `fairSideConviction`. The second payment is made afterward when the function `createConvictionNFT` is called (line 304). At line 50 of the contract `fairSideConviction`, the user transfers `locked` amount of FSD to the contract `fairSideConviction` again.

Similarly, when a user calls `acquireConviction`, he received the amount of locked token twice. The first is at line 123 in the contract `FairSideConviction`, and the second is at line 316 in the contract `ERC20ConvictionScore`.

Referenced code:
When tokenizing convictions:
[ERC20ConvictionScore.sol#L282](https://github.com/code-423n4/2021-05-fairside/blob/main/contracts/dependencies/ERC20ConvictionScore.sol#L282)
[ERC20ConvictionScore.sol#L304](https://github.com/code-423n4/2021-05-fairside/blob/main/contracts/dependencies/ERC20ConvictionScore.sol#L304)
[FairSideConviction.sol#L50](https://github.com/code-423n4/2021-05-fairside/blob/main/contracts/conviction/FairSideConviction.sol#L50)

When acquiring convictions:
[ERC20ConvictionScore.sol#L314](https://github.com/code-423n4/2021-05-fairside/blob/main/contracts/dependencies/ERC20ConvictionScore.sol#L314)
[ERC20ConvictionScore.sol#L316](https://github.com/code-423n4/2021-05-fairside/blob/main/contracts/dependencies/ERC20ConvictionScore.sol#L316)
[FairSideConviction.sol#L123](https://github.com/code-423n4/2021-05-fairside/blob/main/contracts/conviction/FairSideConviction.sol#L123)

## Recommended Mitigation Steps

Should only charge or send FSD tokens once. Consider removing the logic at line 281-285 and 316 in the contract `ERC20ConvictionScore`.
