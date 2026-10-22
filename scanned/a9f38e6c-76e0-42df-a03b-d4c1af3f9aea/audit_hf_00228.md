# [M] Can’t enableCollateral after a disableCollateral

## Summary
Severity: Medium
Contest weight: 0.4323
Dataset id: 1173
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The function `disableCollateral` of OverlayV1Mothership.sol doesn’t set `collateralActive[_collateral] = false;` But it does revoke the roles.

Now `enableCollateral` can never be used because `collateralActive[_collateral] ==true` and it will never pass the second require. So you can never grant the roles again.

Note: `enableCollateral` also doesn’t set `collateralActive[_collateral] = true`

## Proof of Concept
```solidity
function enableCollateral(address _collateral) external onlyGovernor {
    require(collateralExists[_collateral], "OVLV1:!exists");
    require(!collateralActive[_collateral], "OVLV1:!disabled");
    OverlayToken(ovl).grantRole(OverlayToken(ovl).MINTER_ROLE(), _collateral);
    OverlayToken(ovl).grantRole(OverlayToken(ovl).BURNER_ROLE(), _collateral);
}

function disableCollateral(address _collateral) external onlyGovernor {
    require(collateralActive[_collateral], "OVLV1:!enabled");
    OverlayToken(ovl).revokeRole(OverlayToken(ovl).MINTER_ROLE(), _collateral);
    OverlayToken(ovl).revokeRole(OverlayToken(ovl).BURNER_ROLE(), _collateral);
}
```

## Recommendation
In function `enableCollateral()` add the following (after the require): `collateralActive[_collateral] = true;`

In function `disableCollateral` add the following (after the require): `collateralActive[_collateral] = false;`
