# Q1599: freezing user/protocol funds: force a nullifier collision that makes a [when the erc20TokenAddresses a]

## Question
Can an unprivileged attacker force a nullifier collision that makes a victim's future legitimate spend revert forever, where insertNullifiers marks nullifiers[n]=true permanently, to permanently freeze specific user funds or a token's usability in Hinkal, specifically when the erc20TokenAddresses array is reordered (where index-dependent loops behave differently)?

## Target
- File/function: contracts/HinkalBase.sol :: insertNullifiers / insertCommitments / createOnchainCommitment
- Entrypoint: Hinkal.transact / prooflessDeposit
- Attacker controls: nullifier/commitment preimages, deposit volume, token approval state
- Exploit idea: create an irreversible state that blocks a victim's future legitimate action
- Invariant to test: no attacker action can make a victim's own valid future spend permanently revert
- Expected Immunefi impact: Critical: permanent freezing of user funds
- Fast validation: Foundry: trigger the collision/fill, assert the victim's later valid tx reverts
