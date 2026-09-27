# [M] Max allowance might allow tokens in Strategy to be stolen

## Summary
Severity: Medium
Reporter: minhquanym
Source: https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/contracts/strategy/TrueFiStrategy.sol#L74-L76
Type: audit-issue

## Details
# Max allowance might allow tokens in Strategy to be stolen

https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/contracts/strategy/TrueFiStrategy.sol#L74-L76

## Vulnerability Detail
Having residual allowance increases the risk of the asset tokens being stolen from the Strategy contract. Strategy contract is where rewards/assets are held. If the TrueMultiFarm or Euler contract is compromised, it will allow the compromised contract to withdraw funds from the TrueFiStrategy contract due to the residual allowance.

Note that TrueMultiFarm contract is not totally immutable, as it is an upgradeable contract. This is an additional risk factor to be considered. If the TrueFi’s deployer account is compromised, the attacker could upgrade the TrueMultiFarm contract to a malicious one to withdraw funds from the Strategy contract due to the residual allowance.

Sherlock and TrueFi are two separate protocols and teams. Thus, it is a good security practice not to place any trust on external party wherever possible to ensure that if one party is compromised, it won’t affect the other party. Thus, there should not be any residual allowance that allows TrueFi’s contract to withdraw funds from Sherlock’s Strategy contract in any circumstance.

And in this case, TrueFiStrategy even approve `type(uint256).max` amount of USDC and tfUSDC to TrueMultiFarm.

## Impact

USDC and tfUSDC in TrueFiStrategy can be lost

## Proof of Concept

It approved max amount of USDC and tfUSDC to TrueMultiFarm in constructor
```solidity
constructor(IMaster _initialParent) BaseNode(_initialParent) {
  // Approve tfUSDC max amount of USDC
  want.safeIncreaseAllowance(address(tfUSDC), type(uint256).max);
  // Approve tfFarm max amount of tfUSDC
  tfUSDC.safeIncreaseAllowance(address(tfFarm), type(uint256).max);
}
```

## Tool used

Manual Review

## Recommendation

Approve the allowance on-demand whenever _deposit() is called, and reset the allowance back to zero after each minting process to eliminate any residual allowance.
