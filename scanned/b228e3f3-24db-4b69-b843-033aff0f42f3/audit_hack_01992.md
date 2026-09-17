# [M] 6.2 Comments Regarding vow.heal()

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness Medium Version 1 Specification Changed

One of the annotations of the Gate1 contract reads:

- does not execute vow.heal to ensure the dai draw amount from vat.suck is lower than the
    surplus buffer currently held in vow

There is the following comment in Gate1.accessSuck():

```
// call suck to transfer dai from vat to this gate contract
try VatAbstract(vat).suck(address(vow), address(this), amount_) {
// optional: can call vow.heal(amount_) here to ensure
// surplus buffer has sufficient dai balance
```
```
// accessSuck success- successful vat.suck execution for requested amount
return true;
} catch {
```
- vow.heal() uses surplus DAI of the VOW (= surplus buffer) to repay bad debt of the VOW at the
    VAT
- vat.suck() generates DAI by creating bad debt assigned to the VOW

Vat.suck() simply adds bad debt, there is nothing ensuring the amount of DAI drawn is lower than the
surplus buffer.

Specification changed:

The annotation and comments were removed.
