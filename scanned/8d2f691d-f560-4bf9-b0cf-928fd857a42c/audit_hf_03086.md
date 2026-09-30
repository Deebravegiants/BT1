# [M] Uninitialized Strike is allowed to be used

## Summary
Severity: Medium
Contest weight: 0.1962
Dataset id: 17437
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A Strike can either be added when a board is added with createOptionBoard or later
on with addStrikeToBoard. When a Strike is initialized, its id is derived from the
nextStrikeId variable, which is incremented by one for every Strike that is added.
nextStrikeId is set to 1 when the OptionMarket is created. Strike ids are checked for
their validity by comparing Strike.id with the id from the user input that is used to
retrieve the struct from the ​strikes mapping. This check is insufficient for Strike id 0
because, by default, Strike.id is 0, so the check can be bypassed and the Strike is valid
even though it is uninitialized.
The code in _composeTrade performs checks to make sure it only uses a valid Strike.
An invalid Strike can be submitted, though with the id 0. The data structure has not
been initialized as the nextStrikeId starts at 1. So using the id 0 bypasses the check
and then composes TradeParameters based on the uninitialized Strike and
subsequently OptionBoard. While during testing, it was not possible to create a
position with the uninitialized Strike it might be possible under certain circumstances.
The setStrikeSkew function has a similar issue and the Strike id 0 is not rejected.
The owner could accidentally call setStrikeSkew with id 0. With the strike skew set, it
might be possible to create or update a position with invalid Strike values.

## Recommendation
Set nextStrikeId to 0 instead of 1 at contract creation, or add an explicit check to make
sure strikeId 0 is considered invalid and rejected in all the functions listed in the Code
Snippet section.
Checks have been added to ensure strikeId/boardId of 0 cannot be modified even by
admins.
Looks reasonable.
