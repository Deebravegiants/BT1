# [M] The system can get to a “stuck” state if a bad proposal

## Summary
Severity: Medium
Contest weight: 0.2427
Dataset id: 1402
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The LimboDAO contract has a variable that indicates the current proposal - every time there can be only one proposal. The only way a proposal can be done and a new proposal can be registered is to finish the previous proposal by either accepting it and executing it or by rejecting it. If a proposal that can’t succeed, like for example an `UpdateMultipleSoulConfigProposal` proposal that has too much tokens and not enough gas, will stuck the system if it will be accepted. Thats because its time will pass - the users won’t be able to vote anymore (because the `vote` function will revert), and the proposal can’t be executed - the `execute` function will revert. So the proposal won’t be able to be done and the system will be stuck because new proposal won’t be able to be registered.

When trying to call the `executeCurrentProposal()` function that activates the `updateCurrentProposal()` modifier, the modifier will check the balance of fate, it will see that it’s positive and will call `currentProposalState.proposal.orchestrateExecute()` to execute the proposal. the proposal will revert and cancel it all (leaving the proposal as the current proposal with `voting` state).

When trying to call `makeProposal()` function to make a new proposal it will revert because the current proposal is not equal to address(0).

To sum up, the system can get to a “stuck” state if a bad proposal (proposal that can’t be executed) is accepted.

I’m so glad someone finally noticed this. So many issues logged skirted around this issue. A lot of issues were logged about adding too may token to the updateMultipleSoulProposal but the crux of the matter is that the proposal.execute() should be replaced with a call that returns a success boolean so that the DAO doesn’t get stuck on broken proposals. Congratulations on spotting this.

This is a good one, but I’m still going to downgrade this to `medium` as there is no fund at risk afaics.

@jack-the-pug There is a funds risk. Limbo can be paused via flash governance. When paused, funds can’t be withdrawn. The only way to unpause is with a proposal. If the DAO gets jammed up with a broken proposal contract then an attacker can pause Limbo and all staked funds will be locked permanently.

Yeah, I agree that funds can be at risk indirectly, like the vector you described above, but only when the warden made a clear and persuasive presentation about how the funds can be at risk, then it can be a `High`.

Furthermore, this attack vector requires the community to misbehave or at least be imprudent, to pass a malicious proposal, which already lowers the severity of it.

## Recommendation
No recommendation
