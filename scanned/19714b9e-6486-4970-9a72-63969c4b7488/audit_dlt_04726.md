# [M] getPositivePlaceValues(int128) can revert with a small argument

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-09-knox
Published: 2022-10-18
Source: https://github.com/sherlock-audit/2022-09-knox-judging/issues/151
Type: sherlock-finding

## Details
ArbitraryExecution

medium

### getPositivePlaceValues(int128) can revert with a small argument

The key part of this vulnerability is the ruler variable. This is determined by the argument and
can result in a division by zero. The following code shows how this can occur:
        // setup the second place value
        values[1].ruler = ruler / 10;
        values[1].value = (integer / values[1].ruler) % 10;

        // setup the third place value
        values[2].ruler = ruler / 100;
        values[2].value = (integer / values[2].ruler) % 10;

If ruler is less than 10 (or 100 in the second portion of the code) it will result in an operation
the does a integer / 0 operation which would cause a reverted transaction.

A concrete example that shows how this problem could arise is by using an input value of 125. This
result in values[2].ruler being set to 0 (values[2].ruler = ruler / 100; ) which will then cause
a division by zero (values[2].value = (integer / 0) % 10;)

duplicate of #43
