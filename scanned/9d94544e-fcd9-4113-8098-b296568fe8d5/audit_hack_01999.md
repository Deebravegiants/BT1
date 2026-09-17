# [M] 7.3 Rounding Errors In Partial Filling

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Code Corrected

A maker's order can be partially filled according to the following snippet:

```
if (mor.fillWants) {
sor.gives = (offerWants * takerWants) / offerGives;
} else {
sor.wants = (offerGives * takerGives) / offerWants;
}
```
Note that the division can yield rounding errors. The rounding errors can be as extreme as giving funds to
the maker without receiving anything in return or taking from the maker without giving anything back. For
example, consider the case where the maker offers 10 A for 5 B and taker wants to take only 1 A
(fillWants == true). Then, according to the formula she has to offer 5 * 1 / 10 = 0 B.

Code corrected

Prices are now always rounded in favor for the taker to avoid any maker draining. Hence, to calculate
sor.gives when fillWants is true the code has been changed to:


```
uint product = offerWants * takerWants;
sor.gives =
product /
offerGives +
(product % offerGives == 0? 0 : 1);
```
