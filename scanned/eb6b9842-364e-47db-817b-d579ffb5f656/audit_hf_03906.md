# [M] DOS all signatures and verification from agent-

## Summary
Severity: Medium
Contest weight: 0.6937
Dataset id: 20205
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
DOS all signatures and verification from agent-police
Agents need credentials to operate in the pools. This credentials are checked in the modifier called validateAndBurnCred(sc) in the functions from the agent itself.
Overall, this validation ensures that the signature is correctly issued, not expired, not re-used and used by the correct agent Id.
Well, there is a catch. If we go to the modifier:
```solidity
function _validateAndBurnCred(
    SignedCredential calldata signedCredential
) internal {
    agentPolice.isValidCredential(id, msg.sig, signedCredential);
    agentPolice.registerCredentialUseBlock(signedCredential);
}
```
as you can see they are first validating that the signature is fine and all the checks pass and then registering its usage in agent police:
```solidity
function registerCredentialUseBlock(
    SignedCredential memory sc
) external {
    if (IAgent(msg.sender).id() != sc.vc.subject) revert Unauthorized();
    _credentialUseBlock[createSigKey(sc.v, sc.r, sc.s)] = block.number;
}
```
And here we have the critical mistake. In agentPolice, when registering the signature as used, the only check that GLIF makes is if (IAgent(msg.sender).id() != sc.vc.subject) revert Unauthorized(); , there is no access control or whatsoever.
The problem with this check: if (IAgent(msg.sender).id() != sc.vc.subject) revert Unauthorized(); that basically means that the agentId has to be the caller and the same one than the subject param, it is faulty due to Phantom Agents.
What are phantom agents? Well, there is no check for any specific address or nothing stored on the router. Therefore, you can create a contract with the IAgent Interface and create a function with the same selector as id().
This is the first part of the attack.
Second part, front-run the signatures/transactions from the agents to completely leave them in DOS of repaying their debt or borrowing WFIL.
Imagine Agent with id() = 2 wants to pay his debt and calls pay() in its own contract. This agent(the owner of the agent or operator) has to pass the full signature parameters with all the parameters:
SignedCredential calldata sc
It will contain the exact parameters that we need, that are the v,r,s params of the signature.
When we got this params through the mempool, we front-run the transaction of the agent to pay() his debt and in our own malicious IAgent contract, we specify whatever parameters we want in the faulty SignedCredential memory sc but adding the v,r,s from the real agent. This check will go through because we are going to pass a faulty credential with the subject as our fakeID
if (IAgent(msg.sender).id() != sc.vc.subject) revert Unauthorized();
and we are done, the v,r,s params will be set as used:
_credentialUseBlock[createSigKey(sc.v, sc.r, sc.s)] = block.number; and the real agents won't be able to repay is debt
Full DOS of any agents action such as repaying his debt, which will make him fall in a default state

## Recommendation
In the function:
```solidity
function registerCredentialUseBlock(
    SignedCredential memory sc
) external {
    if (IAgent(msg.sender).id() != sc.vc.subject) revert Unauthorized();
    _credentialUseBlock[createSigKey(sc.v, sc.r, sc.s)] = block.number;
}
```
add specific requirements so that the agent is actually a real agent from the system. Maybe fetching the router to check whether they are in a mapping etc.
