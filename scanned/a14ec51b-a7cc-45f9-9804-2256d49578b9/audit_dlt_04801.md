# [H] Anyone can call setCompleted function in Migrations contract

## Summary
Severity: High
Chain: Smart contract
Component: 2022-10-mover
Published: 2022-10-28
Source: https://github.com/sherlock-audit/2022-10-mover-judging/issues/31
Type: sherlock-finding

## Details
cryptphi

high

# Anyone can call setCompleted function in Migrations contract

## Summary
Due to `owner` state variable being hardcoded to `msg.sender` , anyone can call Migrations.setCompleted()

## Vulnerability Detail
The setCompleted() function in Migrations contract implements a modifier to check that the caller is the owner of the contract. However, due to `owner` state variable being hardcoded to `msg.sender` , anyone can call Migrations.setCompleted() and make changes to `last_completed_migration`

## Impact
This is an access control issue.

## Code Snippet
https://github.com/sherlock-audit/2022-10-mover/blob/main/cardtopup_contract/contracts/Migrations.sol#L5-L18

State variable owner
`address public owner = msg.sender;`

Modifier
```solidity
modifier restricted() {
    require(
      msg.sender == owner,
      "This function is restricted to the contract's owner"
    );
    _;
  }
```

Restricted function
```solidity
function setCompleted(uint completed) public restricted {
    last_completed_migration = completed;
  }
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-mover-judging/issues/31_
