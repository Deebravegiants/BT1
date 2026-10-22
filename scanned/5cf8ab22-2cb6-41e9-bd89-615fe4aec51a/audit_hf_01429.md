# [H] `BathToken.sol#_deposit

## Summary
Severity: High
Contest weight: 0.8133
Dataset id: 7388
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
BathToken.sol#_deposit()
```
calculates the actual transferred amount by comparing the before and after balance, however, since there is no reentrancy guard on this function, there is a risk of re-entrancy attack to mint more shares.

Some token standards, such as ERC777, allow a callback to the source of the funds (the `from` address) before the balances are updated in `transferFrom()`. This callback could be used to re-enter the function and inflate the amount.

```solidity
function _deposit(uint256 assets, address receiver)
    internal
    returns (uint256 shares)
{
    uint256 _pool = underlyingBalance();
    uint256 _before = underlyingToken.balanceOf(address(this));

    // **Assume caller is depositor**
    underlyingToken.transferFrom(msg.sender, address(this), assets);
    uint256 _after = underlyingToken.balanceOf(address(this));
    assets = _after.sub(_before); // Additional check for deflationary tokens
    ...
```

## Proof of Concept
With a ERC777 token by using the ERC777TokensSender `tokensToSend` hook to re-enter the `deposit()` function.

Given:

* `underlyingBalance()`: `100_000e18 XYZ`.
* `totalSupply`: `1e18`

The attacker can create a contract with `tokensToSend()` function, then:

1. `deposit(1)`

   - preBalance  = `100_000e18`;
   - `underlyingToken.transferFrom(msg.sender, address(this), 1)`

2. reenter using `tokensToSend` hook for the 2nd call: `deposit(1_000e18)`

   * preBalance = `100_000e18`;
   * `underlyingToken.transferFrom(msg.sender, address(this), 1_000e18)`
   * postBalance = `101_000e18`;
   * assets (actualDepositAmount) = `101_000e18 - 100_000e18 = 1_000e18`;
   * mint `1000` shares;
3. continue with the first `deposit()` call:

   * `underlyingToken.transferFrom(msg.sender, address(this), 1)`
   * postBalance = `101_000e18 + 1`;
   * assets (actualDepositAmount) = `(101_000e18 + 1) - 100_000e18 = 1_000e18 + 1`;
   * mint `1000` shares;

As a result, with only `1 + 1_000e18` transferred to the contract, the attacker minted `2_000e18 XYZ` worth of shares.

## Recommendation
Consider adding `nonReentrant` modifier from OZ’s `ReentrancyGuard`.

Duplicate of [#283](https://github.com/code-423n4/2022-05-rubicon-findings/issues/283) [#410](https://github.com/code-423n4/2022-05-rubicon-findings/issues/410). Note that no ERC777 tokens will be created and this will be patched, making it a non-issue in practice.

Not sure what is meant by “no ERC777 tokens will be created”, since it’s transferring the underlying token which is an arbitrary ERC20, and by extension, ERC777.

The best practice is to break the CEI pattern for deposits and perform the interaction first. Or simply add reentrancy guards.
