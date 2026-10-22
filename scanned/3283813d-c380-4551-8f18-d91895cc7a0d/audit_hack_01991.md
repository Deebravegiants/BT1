# [M] 5.1 Cure.cage() Might Block Shutdown Procedure

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Risk Accepted

The cage function of the Cure contract, when called, requires that live is 1 and sets it to 0 :

```
function cage() external auth {
require(live == 1, "Cure/not-live");
live = 0;
/*...*/
}
```
The function is meant to be called from the End contract :

```
function cage() external auth {
/*...*/
cure.cage();
/*...*/
}
```
If an authorized user (the Governance) were to call the cage function of the Cure contract before the
End contract, then live would be 0, therefore the call to cage would revert, effectively blocking the
shutdown process.

Risk Accepted:

MakerDAO states:

```
We accept this risk as it is, and actually exists in other modules such as the Vow.
We understand each governance action might have important consequences. Each spell
needs to be carefully evaluated.
```
