# [M] 6.4 Gate1.heal()

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Code Corrected

Gate1.heal() is annotated with:

```
// Access to vat.heal() can be used appropriately by an integration
```
It simply calls vat.heal():

```
function heal(uint rad) external {
VatAbstract(vat).heal(rad);
}
```
Vat.heal() heals bad debt of msg.sender()

```
function heal(uint rad) external {
address u = msg.sender;
sin[u] = sub(sin[u], rad);
dai[u] = sub(dai[u], rad);
vice = sub(vice, rad);
debt = sub(debt, rad);
}
```
- The Gate1 contract however doesn't accrue bad debt when generating DAI: Gate1 only draws bad
    debt using vat.suck(address(vow), address(this), amount_). The bad debt is assigned
    to the VOW, only the generated DAI is assigned to the Gate1 contract:

```
function suck(address u, address v, uint rad) external auth {
sin[u] = add(sin[u], rad);
dai[v] = add(dai[v], rad);
vice = add(vice, rad);
debt = add(debt, rad);
}
```
If the Gate1 contract doesn't accrue bad debt outside of its own functionality, the function has no
purpose.

Furthermore, if Gate1 does indeed accrue bad debt, the intended backup DAI balance may be
compromised by the fact that anyone could call heal() and use some of this DAI balance to heal the
bad debt.


Code corrected:

The heal() function of the Gate1 contract was removed.
