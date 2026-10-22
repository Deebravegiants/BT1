# [M] Only `guardian` can change `guardian`

## Summary
Severity: Medium
Contest weight: 0.4888
Dataset id: 18975
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
`guardian` is mentioned as an area of concern in the [docs](https://github.com/code-423n4/2023-07-moonwell#overview):

> Specific areas of concern include:
> 
>   * TemporalGovernor which is the cross chain governance contract. Specific areas of concern include delays, **the pause guardian** , …
> 

`guardian` is a role that has the ability to pause and unpause `TemporalGovernor`. In code, it uses the `owner` from OpenZeppelin `Ownable` as `guardian`. The issue is that [`Ownable::transferOwnership`](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/access/Ownable.sol#L81-L86) is not overridden. Only `guardian` (`owner`) can transfer the role.

This can be a conflict of interest if there is a falling out between governance and the guardian. If the `guardian` doesn’t want to abstain, governance only option would be to call [`revokeGuardian`](https://github.com/code-423n4/2023-07-moonwell/blob/main/src/core/Governance/TemporalGovernor.sol#L205-L221) which sets `owner` to `address(0)`. This permanently removes the ability to pause the contract which can be undesirable.

## Proof of Concept
```solidity
Simple test in `TemporalGovernorExec.t.sol`:
    
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
        governor.executeProposal("");
    }
```

## Recommendation
Consider overriding `transferOwnership` and either limit it to only governance (`msg.sender == address(this)`) or both `guardian` and governance.

This is an interesting finding. Only `guardian` can change `guardian`, however, `guardian` can only pause once and is limited in abilities to being able to fast track execution, and unpause. After a single malicious pause, the `guardian` would no longer be able to pause, and 30 days later, governance would reopen.
