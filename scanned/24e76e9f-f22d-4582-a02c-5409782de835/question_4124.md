# Q4124: freezing user/protocol funds: insert leaves until m_index approaches 2 [when onChainCreation[i] is tru]

## Question
Can an unprivileged attacker insert leaves until m_index approaches 2**LEVELS so the tree fills and blocks all deposits, where insert requires m_index <= 2**LEVELS, to permanently freeze specific user funds or a token's usability in Hinkal, specifically when onChainCreation[i] is true for the affected token (where the RHS of the balance equation drops the amount term)?

## Target
- File/function: contracts/HinkalBase.sol :: insertNullifiers / insertCommitments / createOnchainCommitment
- Entrypoint: Hinkal.transact / prooflessDeposit
- Attacker controls: nullifier/commitment preimages, deposit volume, token approval state
- Exploit idea: create an irreversible state that blocks a victim's future legitimate action
- Invariant to test: no attacker action can make a victim's own valid future spend permanently revert
- Expected Immunefi impact: Critical: permanent freezing of user funds
- Fast validation: Foundry: trigger the collision/fill, assert the victim's later valid tx reverts
