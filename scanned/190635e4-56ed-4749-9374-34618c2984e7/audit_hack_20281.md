# [H] 5.2.9 _removeStackPosition()always reverts

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** High Risk
**Context:** LienToken.sol#L823-L828
**Description:** removeStackPosition()always reverts since it callsstackarray for an index beyond its length:

```
for (i; i < length; ) {
unchecked {
newStack[i] = stack[i + 1];
++i;
}
}
```
Notice that fori==length-1,stack[length]is called. This reverts sincelengthis the length ofstackarray.
Additionally, the intention is to delete the element fromstackat indexpositionand shift left the elements ap-
pearing after this index. However, an addition increment to the loop indexiresults innewStack[position]being
empty, and the shift of other elements doesn't happen.
**Recommendation:** Apply this diff to LienToken.sol#L823-L831:

- unchecked {
- ++i;
- }
- for (i; i < length; ) {
+ for (i; i < length-1; ) {
    unchecked {
       newStack[i] = stack[i + 1];
       ++i;
    }
}


Note: This issue has to be considered in conjunction with the following issue:

- makePaymentdoesn't properly update stack, so most payments don't pay off debt
**Astaria:** Fixed in PRs 202 and 265.
**Spearbit:** Verified.
