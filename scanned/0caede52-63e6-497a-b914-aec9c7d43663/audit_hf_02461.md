# [C] Improper Authorization In changeReduceReserveCaller()

## Summary
Severity: Critical
Contest weight: 0.6182
Dataset id: 13187
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As mentioned earlier, the LEND by TEN Finance protocol is heavily forked from Compound and shares the same architectural design. The protocol extends the cToken contract to support sharing revenue fees of the platform with its token holders. While examining this part of logic, we notice an issue in current implementation.

```solidity
function changeReduceReserveCaller(address newCaller) external {
    require(msg.sender != admin);
    reduceReserveCaller = newCaller;
}

function _reduceReservesFresh(uint reduceAmount) internal returns (uint) {
    uint totalReservesNew;
    // Check caller is reduceReserveCaller
    if (msg.sender != reduceReserveCaller) {
        return fail(Error.UNAUTHORIZED, FailureInfo.REDUCE_RESERVES_ADMIN_CHECK);
    }
    // doTransferOut reverts if anything goes wrong, since we can't be sure if side effects occurred.
    (MathError mathErr, uint halfReduceAmount) = divUInt(reduceAmount, 2);
    if (mathErr != MathError.NO_ERROR) {
        return fail(Error.MATH_ERROR, FailureInfo.REDUCE_RESERVES_VALIDATION);
    }
    doTransferOut(admin, halfReduceAmount);
    doTransferOut(msg.sender, halfReduceAmount);
    emit ReservesReduced(admin, reduceAmount, totalReservesNew);
    return uint(Error.NO_ERROR);
}
```

To elaborate, we show above the changeReduceReserveCaller() and _reduceReservesFresh() routines. We notice the _reduceReservesFresh() routine is used to transfer reserves to admin by the privileged account reduceReserveCaller. However, in the changeReduceReserveCaller() routine, the sanity check is requiring msg.sender != admin when calling this routine, which is giving privilege control to anyone who is NOT the admin!

## Recommendation
Correct the above routine to properly handle the privilege control in the changeReduceReserveCaller() routine.
