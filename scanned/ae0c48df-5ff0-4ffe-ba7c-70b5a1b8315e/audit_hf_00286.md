# [H] `forceUnsponsor

## Summary
Severity: High
Contest weight: 0.6092
Dataset id: 1451
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
if (_force && sponsorAmount > totalUnderlying()) {
        sponsorToTransfer = totalUnderlying();
    } else if (!_force) {
        require(
            sponsorToTransfer <= totalUnderlying(),
            "Vault: not enough funds to unsponsor"
        );
    }
    
    totalSponsored -= sponsorAmount;
    
    underlying.safeTransfer(_to, sponsorToTransfer);
```

When `sponsorAmount > totalUnderlying()`, the contract will transfer `totalUnderlying()` to `sponsorToTransfer`, even if there are other depositors and `totalShares` > 0.

After that, and before others despoiting into the Vault, the Attacker can send `1 wei` underlying token, then cal `deposit()` with 0.1 * 1e18 , since `newShares = (_amount * _totalShares) / _totalUnderlyingMinusSponsored` and `_totalUnderlyingMinusSponsored` is `1`, with a tiny amount of underlying token, `newShares` will become extremly large.

As we stated in issue [#166](https://github.com/code-423n4/2022-01-sandclock-findings/issues/166), when the value of `totalShares` is manipulated precisely, the attacker can plant a bomb, and the contract will not work when the deposit/withdraw amount reaches a certain value, freezing the user’s funds.

However, this issue is not caused by lack of reentrancy protection, therefore it cant be solved by the same solution in issue [#166](https://github.com/code-423n4/2022-01-sandclock-findings/issues/166).

## Recommendation
Consider adding a minimum balance reserve (eg. 1e18 Wei) that cannot be withdrawn by anyone in any case. It can be transferred in alongside with the deployment by the deployer.

This should make it safe or at least make it extremely hard or expensive for the attacker to initiate such an attack.

@gabrielpoca @ryuheimat is this new?

it’s new

yap, it’s interesting. The sponsor really is an issue
