# Q4774: freezing user/protocol funds: mint a commitment whose preimage a victi [when the deposit uses proofles]

## Question
Can an unprivileged attacker mint a commitment whose preimage a victim cannot reproduce, stranding their claimed balance, where createOnchainCommitment lets the caller pick stealth fields, to permanently freeze specific user funds or a token's usability in Hinkal, specifically when the deposit uses prooflessDeposit instead of a proof (where the no-proof mint path is taken)?

## Target
- File/function: contracts/HinkalBase.sol :: insertNullifiers / insertCommitments / createOnchainCommitment
- Entrypoint: Hinkal.transact / prooflessDeposit
- Attacker controls: nullifier/commitment preimages, deposit volume, token approval state
- Exploit idea: create an irreversible state that blocks a victim's future legitimate action
- Invariant to test: no attacker action can make a victim's own valid future spend permanently revert
- Expected Immunefi impact: Critical: permanent freezing of user funds
- Fast validation: Foundry: trigger the collision/fill, assert the victim's later valid tx reverts
