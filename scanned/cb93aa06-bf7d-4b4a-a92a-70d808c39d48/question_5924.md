# Q5924: freezing user/protocol funds: insert leaves until m_index approaches 2 [when the cited root is many ba]

## Question
Can an unprivileged attacker insert leaves until m_index approaches 2**LEVELS so the tree fills and blocks all deposits, where insert requires m_index <= 2**LEVELS, to permanently freeze specific user funds or a token's usability in Hinkal, specifically when the cited root is many batches old (where a stale historical root is used for inclusion)?

## Target
- File/function: contracts/HinkalBase.sol :: insertNullifiers / insertCommitments / createOnchainCommitment
- Entrypoint: Hinkal.transact / prooflessDeposit
- Attacker controls: nullifier/commitment preimages, deposit volume, token approval state
- Exploit idea: create an irreversible state that blocks a victim's future legitimate action
- Invariant to test: no attacker action can make a victim's own valid future spend permanently revert
- Expected Immunefi impact: Critical: permanent freezing of user funds
- Fast validation: Foundry: trigger the collision/fill, assert the victim's later valid tx reverts
