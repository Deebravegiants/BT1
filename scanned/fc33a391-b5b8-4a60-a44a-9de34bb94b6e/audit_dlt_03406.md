# [M] only `guardian` can change `guardian`

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-moonwell
Published: 2023-07-31
Source: https://github.com/code-423n4/2023-07-moonwell-findings/issues/315
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-07-moonwell/blob/main/src/core/Governance/TemporalGovernor.sol#L27
https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/access/Ownable.sol#L81-L86


# Vulnerability details

## Impact
`guardian` is mentioned as an area of concern in the [docs](https://github.com/code-423n4/2023-07-moonwell#overview):
> Specific areas of concern include:
> ...
> * TemporalGovernor which is the cross chain governance contract. Specific areas of concern include delays, **the pause guardian**, ...

`guardian` is a roll that has the ability to pause and unpause `TemporalGovernor`. In code, it uses the `owner` from OpenZeppelin `Ownable` as `guardian`. The issue is that [`Ownable::transferOwnership`](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/access/Ownable.sol#L81-L86) is not overridden. Only `guardian` (`owner`) can transfer the role.

This can be a conflict of interest if there is a falling out between governance and the guardian. If the `guardian` doesn't want to abstain, governance only option would be to call [`revokeGuardian`](https://github.com/code-423n4/2023-07-moonwell/blob/main/src/core/Governance/TemporalGovernor.sol#L205-L221) which sets `owner` to `address(0)`. This permanently removes the ability to pause the contract which can be undesirable.

## Proof of Concept
Simple test in  `TemporalGovernorExec.t.sol`:
```solidity
    function testGovernanceCannotTransferGuardian() public {
        address[] memory targets = new address[](1);
        targets[0] = address(governor);
        uint256[] memory values = new uint256[](1);
        
        bytes[] memory payloads = new bytes[](1);
        payloads[0] = abi.encodeWithSelector(Ownable.transferOwnership.selector,address(newAdmin));

        bytes memory payload = abi.encode(address(governor), targets, values, payloads);
        mockCore.setStorage(true, trustedChainid, governor.addressToBytes(admin), "reeeeeee", payload);

        governor.queueProposal("");

        vm.warp(block.timestamp + proposalDelay);

        // governance cannot transfer guardian
        vm.expectRevert(abi.encodeWithSignature("Error(string)", "Ownable: caller is not the owner"));
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-07-moonwell-findings/issues/315_
