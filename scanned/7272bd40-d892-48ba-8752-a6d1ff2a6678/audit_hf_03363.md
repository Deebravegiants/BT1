# [M] Potential `stake

## Summary
Severity: Medium
Contest weight: 0.6390
Dataset id: 18227
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is an edge‑case denial‑of‑service condition that occurs when the SafETH contract’s totalSupply of derivative tokens is reduced to a single wei. The root cause is a combination of arithmetic that assumes a positive underlying value and a price calculation that can become zero when the contract holds only one wei of SafETH and the underlying derivative price is manipulated to yield an underlyingValue of zero. When this situation arises, the preDepositPrice variable is set to zero in the stake() function because the else branch computes it as (10**18 * underlyingValue) / totalSupply. The subsequent mintAmount calculation divides totalStakeValueEth by this zero price, causing a divide‑by‑zero revert and preventing any new stake from being minted. An attacker who is the sole holder of SafETH can trigger the condition by unstaking totalSupply‑1, leaving exactly one wei in circulation. If the derivative’s ethPerDerivative price is artificially lowered (for example via an AMM manipulation) so that underlyingValue evaluates to zero, the contract reaches the fatal state. The impact is that future users attempting to stake receive a transaction revert, see no tokens minted, and may perceive that the protocol is broken or that their funds are lost. This occurs only under the specific condition of totalSupply equal to one wei and underlyingValue equal to zero, which is unlikely in normal operation but can be forced by a malicious participant. The affected parties are prospective stakers and the protocol itself, because the inability to accept new deposits halts growth and may require a contract redeployment. The issue was discovered during a formal audit by examining the stake() arithmetic and constructing a proof‑of‑concept that forces preDepositPrice to zero, revealing the divide‑by‑zero revert. It is hard to notice because typical test scenarios never reach a totalSupply of one wei, and the price manipulation required is subtle. To remediate, the deployment process should ensure that at least one derivative token with a non‑zero weight is minted (for example by performing an initial stake of 0.5 ETH) so that totalSupply never drops to the critical value. Alternatively, the unstake() function can enforce a minimumSupply threshold, preventing totalSupply from falling below a safe bound. Conceptually, the fix is to guarantee that the denominator in the price calculation is never zero, either by initializing the contract with a positive supply or by adding explicit checks that reject operations that would reduce the supply to the dangerous range. This prevents the contract from entering a state where staking reverts, preserving normal user experience and protocol functionality.

## Proof of Concept
The goal of this POC is to prove that this line can revert <https://github.com/code-423n4/2023-03-asymmetry/blob/44b5cd94ebedc187a08884a7f685e950e987261c/contracts/SafEth/SafEth.sol#L98>

```solidity
uint256 mintAmount = (totalStakeValueEth * 10 ** 18) / preDepositPrice;
```

This can occur if the attacker can cause `preDepositPrice = 0`.

A user who is the first staker will be the sole holder of 100% of `totalSupply` of safETH.

They can then unstake (and therefore burn) `totalSupply - 1` leaving a total of 1 wei of safETH in circulation.

In earlier lines in `stake()` <https://github.com/code-423n4/2023-03-asymmetry/blob/44b5cd94ebedc187a08884a7f685e950e987261c/contracts/SafEth/SafEth.sol#L77-L81>, we see

```solidity
uint256 totalSupply = totalSupply();
uint256 preDepositPrice; // Price of safETH in regards to ETH
if (totalSupply == 0)
    preDepositPrice = 10 ** 18; // initializes with a price of 1
else preDepositPrice = (10 ** 18 * underlyingValue) / totalSupply;
```

With `totalSupply = 1`, we see that the above code block will execute the `else` code path, and that if `underlyingValue = 0`, then `preDepositPrice = 0`.

`underlyingValue` is set in earlier lines: <https://github.com/code-423n4/2023-03-asymmetry/blob/44b5cd94ebedc187a08884a7f685e950e987261c/contracts/SafEth/SafEth.sol#L68-L75>

```solidity
uint256 underlyingValue = 0;

// Getting underlying value in terms of ETH for each derivative
for (uint i = 0; i < derivativeCount; i++)
    underlyingValue +=
        (derivatives[i].ethPerDerivative(derivatives[i].balance()) *
            derivatives[i].balance()) /
        10 ** 18;
```

For a simple case, assume there is 1 derivative with 100% weight. Let’s use rETH for this example since the derivative can get its `ethPerDerivative` price from an AMM. In this case:

  * Assume the `ethPerDerivative()` value has been manipulated in the underlying AMM pool such that 1 derivative ETH is worth less than 1 ETH. eg: 1 rETH = 9.99…9e17 ETH
  * In this case, also assume that since there is 1 wei of safETH circulating, there should be 1 wei of ETH staked through the protocol, and therefore `derivatives[i].balance() = 1 wei`.

This case will result in `underlyingValue += (9.99...9e17 * 1) / 10 ** 18 = 0`.

We can see that it is therefore possible to cause a divide by 0 revert and malfunction of the `stake()` function.

## Recommendation
Assuming the deployment process will set up at least 1 derivative with a weight, simply adding a `stake()` operation of 0.5 ETH as the first depositor as part of the deployment process avoids the case where safETH totalSupply drops to 1 wei.

Otherwise, within `unstake()` it is also possible to require that `totalSupply` does not fall between 0 and `minimumSupply` where `minimumSupply` is, for example, the configured `minAmount`.

Seems like a pretty big edge case and it would leave the contract with basically no funds which doesn’t seem like a High severity to me.

Indeed, the described scenario isn’t of high severity although the finding is valid. Basically, the first or last SafETH user could force the owner to redeploy, so downgrading to Medium. 

Out of scope for mitigation review. We will be manually holding safETH to prevent this, if not redeploy.
