# Q0699: freezing user/protocol funds: force a nullifier collision that makes a [when a prior tx in the same bl]

## Question
Can an unprivileged attacker force a nullifier collision that makes a victim's future legitimate spend revert forever, where insertNullifiers marks nullifiers[n]=true permanently, to permanently freeze specific user funds or a token's usability in Hinkal, specifically when a prior tx in the same block left the action or tree in a partial state (where cross-tx residual state carries over)?

## Target
- File/function: contracts/HinkalBase.sol :: insertNullifiers / insertCommitments / createOnchainCommitment
- Entrypoint: Hinkal.transact / prooflessDeposit
- Attacker controls: nullifier/commitment preimages, deposit volume, token approval state
- Exploit idea: create an irreversible state that blocks a victim's future legitimate action
- Invariant to test: no attacker action can make a victim's own valid future spend permanently revert
- Expected Immunefi impact: Critical: permanent freezing of user funds
- Fast validation: Foundry: trigger the collision/fill, assert the victim's later valid tx reverts
