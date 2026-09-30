# [H] Missing highestVotingPower Update

## Summary
Severity: High
Contest weight: 0.4085
Dataset id: 23086
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The argmaxBlockByStake function is used to identify the block height with the highest cumulative voting power based on the stakes of voting reputers. However, the calculation for highestVotingPower is flawed. The function updates blockOfMaxPower when finding a new block with higher voting power but fails to update highestVotingPower. This results in incorrect block selection. The following code snippet from argmaxBlockByStake illustrates the issue. Lines 13 and 14 properly calculate the voting power blockVotingPower for each block. However, when a new highest voting power is found, only blockOfMaxPower is updated while highestVotingPower is not, leading to erroneous results.
```go
func (ap *AppChain) argmaxBlockByStake(
blockToReputer *map[int64][]string,
stakesPerReputer map[string]cosmossdk_io_math.Int,
) int64 {
// Find the current block height with the highest voting power
firstIter := true
highestVotingPower := cosmossdk_io_math.ZeroInt()
blockOfMaxPower := int64(-1)
for block, reputersWhoVotedForBlock := range *blockToReputer {
// Calc voting power of this candidate block by total voting reputer stake
blockVotingPower := cosmossdk_io_math.ZeroInt()
for _, reputerAddr := range reputersWhoVotedForBlock {
blockVotingPower = blockVotingPower.Add(stakesPerReputer[reputerAddr])
}
// Decide if voting power exceeds that of current front-runner
if firstIter || blockVotingPower.GT(highestVotingPower) {
blockOfMaxPower = block // Correctly updates the block
// Missing highestVotingPower = blockVotingPower
}
firstIter = false
}
return blockOfMaxPower
}
```
The function will incorrectly identify the block with the greatest cumulative voting power. This could have downstream effects, such as incorrect block selection, mishandling of stakes, and potential inconsistencies in subsequent processing or decision-making based on these results.

## Recommendation
To resolve this issue, update highestVotingPower whenever blockOfMaxPower is updated:
```go
func (ap *AppChain) argmaxBlockByStake(
blockToReputer *map[int64][]string,
stakesPerReputer map[string]cosmossdk_io_math.Int,
) int64 {
firstIter := true
highestVotingPower := cosmossdk_io_math.ZeroInt()
blockOfMaxPower := int64(-1)
for block, reputersWhoVotedForBlock := range *blockToReputer {
blockVotingPower := cosmossdk_io_math.ZeroInt()
for _, reputerAddr := range reputersWhoVotedForBlock {
if stake, exists := stakesPerReputer[reputerAddr]; exists {
// Ensure reputer has a valid stake
blockVotingPower = blockVotingPower.Add(stake)
} else {
ap.Logger.Warn().Str("reputerAddr", reputerAddr).Msg("Reputer address not found in stake map")
}
}
if firstIter || blockVotingPower.GT(highestVotingPower) {
highestVotingPower = blockVotingPower
// Update the highest voting power
blockOfMaxPower = block
// Correctly updates the block
}
firstIter = false
}
// Log warning if no block was found with positive voting power
if highestVotingPower.IsZero() {
ap.Logger.Warn().Msg("No block found with positive voting power.")
}
return blockOfMaxPower
}
```
