# [M] Improper i256::rescale() Logic

## Summary
Severity: Medium
Contest weight: 0.5714
Dataset id: 11915
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Deri-V4 protocol has the built-in arithmetic operation support for unsigned integers (with the so-called I256 type). While reviewing the I256 type support, we notice one core rescale() routine has an incorrect implementation.
```solidity
public fun rescale(num: I256, decimals_s1: u8, decimals_s2: u8): I256 {
    if (decimals_s1 == decimals_s2) {
        num
    } else {
        neg_from(
            abs_u256(num) *
            (math64::pow(10, (decimals_s2 as u64)) as u256) /
            (math64::pow(10, (decimals_s1 as u64)) as u256)
        )
    }
}
```
To elaborate, we show above the implementation of this specific rescale() routine. This routine has a rather straightforward logic in adjusting the given I256 num from the first decimal decimals_s1 to the second decimal decimals_s2. When these two decimals are different, it always returns the negative number, which is apparently incorrect. A suggestion revision is shown as follows:
```solidity
public fun rescale(num: I256, decimals_s1: u8, decimals_s2: u8): I256 {
    if (decimals_s1 == decimals_s2) {
        num
    } else {
        let rescaled_num = abs_u256(num) *
            (math64::pow(10, (decimals_s2 as u64)) as u256) /
            (math64::pow(10, (decimals_s1 as u64)) as u256);
        if (sign(num) == 1) {
            neg_from(rescaled_num)
        } else { rescaled_num }
    }
}
```

## Recommendation
Improve the above routine to properly adjust an I256 num from one decimal to another.
