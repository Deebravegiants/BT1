# [M] Non-whitelisted owner can also hold/own a troveNFT

## Summary
Severity: Medium
Contest weight: 0.5688
Dataset id: 2427
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a user opens a trove, troveNFT is minted to owner and it requires the owner to be whitelisted i.e. non-whitelisted owners are not allowed to mint/own the troveNFT.

```solidity
function openTrove(
    address _owner,
    uint256 _ownerIndex,
    uint256 _collAmount,
    uint256 _boldAmount,
    uint256 _upperHint,
    uint256 _lowerHint,
    uint256 _annualInterestRate,
    uint256 _maxUpfrontFee,
    address _addManager,
    address _removeManager,
    address _receiver
) external override returns (uint256) {
    _requireValidAnnualInterestRate(_annualInterestRate);

    IWhitelist _whitelist = whitelist;
    if (address(_whitelist) != address(0)) {
        _requireWhitelisted(_whitelist, _owner);
        _requireWhitelisted(_whitelist, msg.sender);
        if (_receiver != address(0)) {
            _requireWhitelisted(whitelist, _receiver);
        }
    }

    ....
}
```

```solidity
function onOpenTrove(
    address _owner,
    uint256 _troveId,
    TroveChange memory _troveChange,
    uint256 _annualInterestRate
) external {
    ....

    // mint ERC721
    troveNFT.mint(_owner, _troveId);

    ....
}
```

However, this whitelist requirement can be bypassed because troveNFTs are transferable and a whitelisted owner can transfer his troveNFT to a non-whitelisted owner, bypassing the whitelist requirement.

## Recommendation
No recommendation
