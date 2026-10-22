# [H] MJR-1 Invalid setter function

## Summary
Severity: High
Contest weight: 0.0665
Dataset id: 13573
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the setDefaultController() function defined at line PieFactoryContract.sol#L34, the new value is assigned to the defaultController variable. But it is not taken into account that earlier using the bakePie() function, the pool owner could be changed to address of defaultController. Thus, as a result of the work of the setDefaultController() function, the pool owner will remain the same, while it is expected that the pool will be managed from a different address.
In the setFeeBeneficiary() function defined at line BasketFacet.sol#L87, the LibBasketStorage.basketStorage().FeeBeneficiary variable is assigned a new value. But it is not taken into account that earlier tokens could be issued to this address in the following places: BasketFacet.sol#L141, BasketFacet.sol#L175, BasketFacet.sol#L216.

## Recommendation
It is necessary to carefully check the logic of these functions and make corrections if necessary.
