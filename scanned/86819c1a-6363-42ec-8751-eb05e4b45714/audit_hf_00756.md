# [M] SiloVault will incorrectly accrue rewards during user transfer/transferFrom actions due to unsynced totalSupply

## Summary
Severity: Medium
Contest weight: 0.6445
Dataset id: 2346
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
SiloVault’s totalSupply() [accrueFees](https://github.com/code-423n4/2025-03-silo-finance/blob/0409be5b85d7aabfbbe10de1de1890d4b862d2d5/silo-vaults/contracts/SiloVault.sol#L944) from interests (delta totalAssets). Such fee accrual is updated through _accrueFee() which mints an additional share to the fee reciever.

We see that when claiming rewards directly through `claimRewards()` the accrued extra share is updated first before _claimRewards().

The vulnerability is when `_claimRewards()` is invoked atomically through hooks (_update), the `_accrueFee()` will be missed in the user’s transfer/transferFrom call. In this case, an incorrect totalSupply() will be used for fee accrual, leading to incorrect fee accrual.

Impacts: incorrect and inconsistent reward accrual due to unsynced `totalSupply()`.

## Proof of Concept
We see in direct `claimRewards` flow. `totalSupply()` will be updated in `_accrueFee()`.

```solidity
function claimRewards() public virtual {
    _nonReentrantOn();

    _updateLastTotalAssets(_accrueFee());
    _claimRewards();

    _nonReentrantOff();
}

function _accrueFee() internal virtual returns (uint256 newTotalAssets) {
    uint256 feeShares;
    (feeShares, newTotalAssets) = _accruedFeeShares();
    // @audit this will increase totalSupply()
    if (feeShares != 0) _mint(feeRecipient, feeShares);

    emit EventsLib.AccrueInterest(newTotalAssets, feeShares);
}
```

However, the vulnerable flow is transfer/transferFrom -> _update(), where `_accrueFee()` is missed.

```solidity
function _update(address _from, address _to, uint256 _value) internal virtual override {
    // on deposit, claim must be first action, new user should not get reward

    // on withdraw, claim must be first action, user that is leaving should get rewards
    // immediate deposit-withdraw operation will not abused it, because before deposit all rewards will be
    // claimed, so on withdraw on the same block no additional rewards will be generated.

    // transfer shares is basically withdraw->deposit, so claiming rewards should be done before any state changes

    _claimRewards(); // @audit rewards is claimed without first updating totalSupply(). transfer/transferFrom flow is vulnerable.

    super._update(_from, _to, _value);

    if (_value == 0) return;

    _afterTokenTransfer(_from, _to, _value);
}
```

We know transfer/transferFrom flow is vulnerable because unlike deposit/withdraw which calls `_accrueFee()` first, transfer/transferFrom will directly call `_update()` without updating totalSupply. This causes an incorrect/inconsistent reward accrual.

IhorSF (Silo Finance) disputed

This PR [here](https://github.com/silo-finance/silo-contracts-v2/pull/1168) fixes the accrue on transfer for SiloVault.

## Recommendation
No recommendation
