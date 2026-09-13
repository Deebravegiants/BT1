# [H] 6.2.2 Order of calls toremoveValidatorscan affect the resulting validator keys set

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** High Risk

**Context:** OperatorsRegistry.1.sol#L

**Description:** If two entitiesAandB(which can be either theadminor the operatorOwith the indexI) send a call
toremoveValidatorswith 2 different set of parameters:

- T 1 : (I,R 1 )
- T 2 : (I,R 2 )

Then depending on the order of transactions, the resulting set of validators for this operator might be different. And
since either party might not know a priori if any other transaction is going to be included on the blockchain after
they submit their transaction, they don't have a 100 percent guarantee that their intended set of validator keys are
going to be removed.

This also opens an opportunity for either party to DoS the other party's transaction by frontrunning it with a call to
remove enough validator keys to trigger theInvalidIndexOutOfBoundserror:

OperatorsRegistry.1.sol#L324-L326:

```
if (keyIndex >= operator.keys) {
revert InvalidIndexOutOfBounds();
}
```
**Recommendation:** We can send a snapshot block parameter to removeValidators and compare it
to a stored field for the operator and make sure there have not been any changes to the validator key
set since that snapshot block. Alluvial has introduced such a mechanism for setOperatorLimits in
030b52feb5af2dd2ad23da0d512c5b0e55eb8259. A similar technique can be used here.

**Alluvial:** Don't think this is really an issue.

On a regular basis, the admin would not remove the keys but would request the Node Operator to remove the
keys (because a key is unhealthy for example). In case a Node Operator refuses to remove the key (which is
unexpected because this is would be against terms and conditions) then the admin could deactivate the operator
and then remove the key without being exposed to the front run attack.

This is not as sensitive as the front run we had onsetOperatorLimitbecause in this case, we are not making
any keys eligible for funding. So the consequences are not this bad. Worst case the admin deactivates the node
operator and there is no issue anymore.

**Spearbit:** We think the issue still needs to be documented both for theadminand also for the operators. Because
in the scenario above bothAandBcan be the operatorO. AndOmight send two transactionsT 1 ,T 2 thinkingT 1
would be applied to the state beforeT 2 (this might be unintentional, or intentional maybe because of something
like out-of-gas issues). But it is possible that the order would be reversed and the end result would not be what the
operator had expected. And if the operator would not check this, the issue can go unnoticed.
