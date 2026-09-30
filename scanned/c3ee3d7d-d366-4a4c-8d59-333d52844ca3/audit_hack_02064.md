# [H] 7.3 Incorrect Maximum Collateral Amount

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness High Version 1 Code Corrected

The function _testMaxCAmount computes the "Maximum amount of collateral that can be insured".
This is computed as follows:

```
1.The stocksUsers variable is queried from the StableMaster contract.
2.The amount of minted stable coins is queried from the StableMaster contract and converted into
a collateral amount using the current rate.
3.The smaller of the two values above is multiplied with maxALock (the maximum percentage to be
insured) and then returned.
```
Both of these values are sometimes incorrect and hence shouldn't be used for the calculation:

```
1.stocksUsers is defined as:
```

```
// Amount of collateral in the reserves that comes from users
// + capital losses from HAs - capital gains of HAs
```
```
Due to the capital losses and capital gains it might be bigger or smaller than needed for the present
calculation. Consider the following example:
After a late liquidation stocksUsers = 15 ETH, with a rate of 500, but previously 10,000 stable
coins have been minted. The system needs to insure 20 ETH, but would return 15 ETH * maxALock.
2.The amount of minted stable coins can only be used for this calculation if only a single collateral is
used for this stable coin. However, multiple collaterals might be available to mint this stable coin and
hence the system would calculate an incorrect amount of insurable collateral.
```
Code corrected:

Now, the stocksUsers variable represents the amount of stablecoins minted per collateral and the
system separates the stable coins minted against different collaterals. For more information see the
description of System Accounting.
