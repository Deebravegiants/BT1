# [M] Possible to mint or burn infinite shares, stealing all rewards or making transfers fail

## Summary
Severity: Medium
Contest weight: 0.1874
Dataset id: 16157
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Increasing shares infinitely allows an attacker to steal all rewards. It’s possible by doing:
1. In _isExcludedFromRewards(), the condition addr.code.length > 0 && !isOptin[addr] will return false if the contract is in the constructor, enabling - 1. transfer Trestle no a new contract, 2. after the constructor, move the funds to another address, which won't reduce shares as the contract has not opted in.
2. Calling rewardOptIn() with a blacklisted address will increase shares infinitely as _isExcludedFromRewards() will always return true, increasing shares every time (not possible anymore as addresses can not be blacklisted post dead block period).
3. Removing from the blacklist a smart contract that has not opted in will keep increasing shares every time, as _isExcludedFromRewards() will always return true.
Decreasing shares to 0 will mean reward eligible accounts (EOAs or smart contracts that have opted in) with previous non 0 balance will always revert when transferring shares (either from or to). It’s possible to do this in the 2 following aways:
1. rewardOptout() will keep decreasing shares if called by an EOA or in the constructor of a smart contract, as _isExcludedFromRewards() will always return false.
2. _addToBlacklist() will keep decreasing shares if addr is an EOA or a smart contract that has opted in, as will always return false (not possible anymore as the dead block period is over).

## Recommendation
Recommendation not found
