# [M] Possible index out of range in GetVoterIndex could cause ballot to never finalize due to panic

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-11-zetachain
Published: 2023-11-27
Source: https://github.com/code-423n4/2023-11-zetachain-findings/issues/116
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/observer/types/ballot.go#L27-L35


# Vulnerability details

## Description
The function `GetVoterIndex` is used in multiple places to get the index of a specific Observer from the Voter List. The problem is that the caller is assuming the function will always succeed, but clearly there is a possibility where the `Observer address could not be found`, which would return an `index of -1`, which will effectivelly make the program panic.


```golang
func (m Ballot) GetVoterIndex(address string) int {
	index := -1
	for i, addr := range m.VoterList {
		if addr == address {
			return i
		}
	}
	return index
}
```

#### **[Instance 1]**
##### `Observer::BallotByIdentifier`
This one is safe since the GetVoterIndex is called from the same ballot instance it is iterating over, so it's impossible to not find the index in such case.
```golang
	for i, voterAddress := range ballot.VoterList {
		voter := types.VoterList{
			VoterAddress: voterAddress,
			VoteType:     ballot.Votes[ballot.GetVoterIndex(voterAddress)],
		}
		votersList[i] = &voter
	}
```
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/observer/keeper/ballot.go#L94



_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-11-zetachain-findings/issues/116_
