# [M] 5.1 Circumvention of Ramping

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Code Partially Corrected

The management account of Pool can initiate a change of asset weights or the amplification factor for a
pool. The change should be applied slowly to minimize profits from sandwiching attacks, see
Sandwiching Curve changes. However, the function add_asset allows the management to modify
(reduce) the weights of assets and the amplification factor by avoiding the ramping limitations entirely.
The natspec description of the function notes:

```
@dev Every other asset will have their weight reduced pro rata
@dev Caller should assure that effective amplification before and after call are the same
```
Code partially corrected:

The function add_asset now sets an upper limit of 1% on the initial weight of the new asset being added
to the pool. Although this reduces the likelihood of accidentally changing the weights of assets


significantly, it does not enforce any restriction on the amplification factor (_amplification represents
the term A * f^n in the whitepaper). Therefore, management should consider sandwiching attacks
when calling this function and carefully choose input parameters. The response of Yearn is:

```
Added a limit to the new asset weight, it is not allowed to exceed 1%. Since
the `amplification` in the pool represents 'A * f^n', we cannot easily put
bounds on the amplification factor. It is up to the management role to make sure
the call cannot be sandwiched, either by picking a new amplification factor and
initial weight (even lower than 1%) that minimises the effect or by first pausing
the pool and in a separate call add the asset before unpausing.
```
