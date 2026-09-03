# Q5698: factory deployment: abuse that deployHinkal transfers owners [when the tree has exactly one ]

## Question
Can an unprivileged attacker abuse that deployHinkal transfers ownership and grants DEFAULT_ADMIN_ROLE to msg.sender then renounces the factory's, to hijack the deterministic Hinkal address, deploy attacker bytecode at it, or permanently block the intended deployment, specifically when the tree has exactly one prior leaf (where roots[MINIMUM_INDEX] equals that leaf directly)?

## Target
- File/function: contracts/HinkalFactory.sol :: deployHinkal / appendBytecodeChunk / HinkalFactoryDeployer
- Entrypoint: HinkalFactoryDeployer constructor / HinkalFactory (pre-ownership)
- Attacker controls: create2 salt via SAFE_SINGLETON_FACTORY, deployment ordering (only if reachable pre-owner)
- Exploit idea: race or corrupt the deterministic deployment before ownership is settled
- Invariant to test: the code at the deterministic Hinkal address == the audited Hinkal bytecode
- Expected Immunefi impact: Critical: permanent freezing of user funds
- Fast validation: Foundry: simulate the create2 race/hash mismatch, assert wrong code or blocked deploy
