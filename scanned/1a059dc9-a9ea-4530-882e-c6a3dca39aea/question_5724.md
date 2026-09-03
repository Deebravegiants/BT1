# Q5724: freezing user/protocol funds: cause a token's approve pattern to leave [when the tree has exactly one ]

## Question
Can an unprivileged attacker cause a token's approve pattern to leave a non-zero residual blocking future safeApprove, where approveERC20Token sets 0 then value; a stuck allowance can revert later approvals, to permanently freeze specific user funds or a token's usability in Hinkal, specifically when the tree has exactly one prior leaf (where roots[MINIMUM_INDEX] equals that leaf directly)?

## Target
- File/function: contracts/HinkalBase.sol :: insertNullifiers / insertCommitments / createOnchainCommitment
- Entrypoint: Hinkal.transact / prooflessDeposit
- Attacker controls: nullifier/commitment preimages, deposit volume, token approval state
- Exploit idea: create an irreversible state that blocks a victim's future legitimate action
- Invariant to test: no attacker action can make a victim's own valid future spend permanently revert
- Expected Immunefi impact: Critical: permanent freezing of user funds
- Fast validation: Foundry: trigger the collision/fill, assert the victim's later valid tx reverts
