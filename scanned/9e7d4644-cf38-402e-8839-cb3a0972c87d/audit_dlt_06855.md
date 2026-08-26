# [H] Loss of vested amounts

## Summary
Severity: High
Chain: Smart contract
Component: 2022-09-vtvl
Published: 2022-09-23
Source: https://github.com/code-423n4/2022-09-vtvl-findings/issues/475
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-09-vtvl/blob/f68b7f3e61dad0d873b5b5a1e8126b839afeab5f/contracts/VTVLVesting.sol#L418
https://github.com/code-423n4/2022-09-vtvl/blob/f68b7f3e61dad0d873b5b5a1e8126b839afeab5f/contracts/VTVLVesting.sol#L147-L151
https://github.com/code-423n4/2022-09-vtvl/blob/f68b7f3e61dad0d873b5b5a1e8126b839afeab5f/contracts/VTVLVesting.sol#L364


# Vulnerability details

## Impact

Vesting is a legal term that means the point in time where property is earned or gained by some person.
The VTVLVesting contract defines:
- a start time (Claim::startTimestamp) and an end time (Claim::endTimestamp) at which vesting starts and ends for a entitled user
- the calculated points in time when the fractions of the total amount are released and therefore can be withdrawn (which are defined by Claim::releaseIntervalSecs).
The entitled user can either withdraw after each interval elapses, or after the whole vesting period is over or any variant of the two options.

The administrator of the contract can revoke the claim for a user at any time, which for vesting assets is expected. For example an employee with a vesting stock allocation of 1000 shares vesting at each quarter over a period of 4 years, may resign after 2 years and therefore the only half of the shares would be vested and therefore sold by the employee. The employee can either sell them at each quarter, or before, or after resigning, in any case the half of the shares have vested and are by legal right owned by the employee.

The VTVLContract revoke has the following defects:
- it ignores the amount already vested and now yet withdrawn
- if called, say half-way the total period, just after claimer withdraws the already vested amount, it revokes only the right to vest the remaining part in future.
- if called, say half-way the total period, right before the claimer withdraws the already vested amount, it revokes both the already vested amount and the right to vest the remaining part in future.

Raising as high impact because it actually causes:
- loss of already vested amounts of a user with a valid claim that has already righteously vested a part but not withdrawn
- different outcomes depending on the order in which withdraw and revokeClaim functions are called which means that one of the two behavoiurs is certainly in conflict with the other causing a loss on one of the two sides, contract or claimer (by definition of Vesting rights, the claimer).
- lack of trust by the potential claimers/users whch can be at any time deprived of righteously vested amounts.

## Proof of Concept

The following two tests prove the behaviour difference when the order by which revokeClaim vs withdraw are called, whch shows that the vesting right is not guaranteed.

```solidity
  // NOTE: USES ORIGINAL REVOKE BEHAVIOUR
  it('sample revoke use case USER LOSE: employee withdraw immediately after resignation', async () => {
    const {tokenContract, vestingContract} = await createPrefundedVestingContract({tokenName, tokenSymbol, initialSupplyTokens});

```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2022-09-vtvl-findings/issues/475_
