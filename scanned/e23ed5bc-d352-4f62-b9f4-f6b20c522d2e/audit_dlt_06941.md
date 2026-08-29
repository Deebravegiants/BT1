# [H] Able to mint any amount of PT

## Summary
Severity: High
Chain: Smart contract
Component: 2022-06-illuminate
Published: 2022-06-26
Source: https://github.com/code-423n4/2022-06-illuminate-findings/issues/349
Type: code-finding

## Details
# Lines of code

[Lender.sol#L192-L235](https://github.com/code-423n4/2022-06-illuminate/blob/main/lender/Lender.sol#L192-L235)
[Lender.sol#L486-L534](https://github.com/code-423n4/2022-06-illuminate/blob/main/lender/Lender.sol#L486-L534)
[Lender.sol#L545-L589](https://github.com/code-423n4/2022-06-illuminate/blob/main/lender/Lender.sol#L545-L589)


# Vulnerability details

## Impact

Some of the ```lend``` functions do not validate addresses sent as input which could lead to a malicous user being able to mint more PT tokens than they should.

Functions affect:

- [Illuminate and Yield ```lend``` function](https://github.com/code-423n4/2022-06-illuminate/blob/main/lender/Lender.sol#L192-L235).

- [Sense ```lend``` function](https://github.com/code-423n4/2022-06-illuminate/blob/main/lender/Lender.sol#L486-L534).

- [APWine ```lend``` function](https://github.com/code-423n4/2022-06-illuminate/blob/main/lender/Lender.sol#L545-L589).

## Proof of Concept

In the Illuminate and Yield ```lend``` function:

1. Let the Yieldspace pool ```y``` be a malicious contract that implements the ```IYield``` interface.

2. The ```base``` and ```maturity``` functions for ```y``` may return any value so the conditions on lines 208 and 210 are easily passed.

3. The caller of ```lend``` sends any amount ```a``` for the desired underlying ```u```.

4. If principal token ```p``` corresponds to the Yield principal, then the ```yield``` function is called which has a [return value controlled by the malicious contract ```y```](https://github.com/code-423n4/2022-06-illuminate/blob/main/lender/Lender.sol#L648).

5. The ```mint``` function is then called for the principal token with an underlying ```u``` and a maturity ```m``` which will then mint the ```returned``` amount of principal tokens to the malicious user.



In the Sense ```lend``` function:

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2022-06-illuminate-findings/issues/349_
