# [M] [PNM-004] Calculation of `_secondaryReserveRatio` can be overflowed

## Summary
Severity: Medium
Contest weight: 0.1495
Dataset id: 12360
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
`uint32 _secondaryReserveRatio = uint32((msg.value * SCALE * 1e18) / (_initialTokenSupply * _initialTokenPrice));`

`_secondaryReserveRatio` can be overflowed by setting a relatively small `_initialTokenSupply` and `_initialTokenPrice`. The result will be truncated by `uint32`, causing an overflow.

This overflow can bypass all the checks in function `initialize`. Any following functionality will be impacted since the `_secondaryReserveRatio` is incorrect.

## Proof of Concept
* The user provide `_initialTokenSupply` and `_initialTokenPrice`, which meets `SCALE * 1e18 == _initialTokenSupply * _initialTokenPrice`
* The `msg.value` is set as `2 ** 32 + X`, where `MIN_SECONDARY_RESERVE_RATIO <= X <= primaryReserveRatio`. Note that `msg.value` is in Wei, so the deposited fund is not huge.

## Recommendation
Add overflow checks.

OpenZeppelin has safe cast helpers that could be leveraged here.

It is concerning that due to the truncation here, the configuration would not work how the user expects given the input parameters. And at this point the NFT has been escrowed into the vault. Because of this it seems Medium risk is a fair assessment.
