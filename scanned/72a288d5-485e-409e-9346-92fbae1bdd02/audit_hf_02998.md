# [M] `Heart::beat`

## Summary
Severity: Medium
Contest weight: 0.1023
Dataset id: 16732
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
`beat()` function is allowed to be called by anyone once in `frequency()` period. The purpose of it is to update the prices and do another operations related to bond market. User who ran it are rewarded. There is no need to run this function more then 1 time in `frequency()` period. However if `beat()` was last time called more then `frequency()` time ago then user can execute `beat()` function `(block.timestamp - lastBeat)/frequency()` times in a row in same block and get rewards.

## Recommendation
Change this line to `lastBeat = block.timestamp - (block.timestamp - lastBeat) % frequency();`  
So no matter how much time the `beat()` was not called, it is possible to call it only once per `frequency()`.

See comment on [#405](https://github.com/code-423n4/2022-08-olympus-findings/issues/405#issuecomment-1239878294). This approach actually solves both of our issues though.

Going to use this issue as the primary since the solution is elegant and solves the problem.
