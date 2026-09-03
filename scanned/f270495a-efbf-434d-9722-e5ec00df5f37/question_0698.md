# Q0698: factory deployment: front-run HinkalFactoryDeployer's SAFE_S [when a prior tx in the same bl]

## Question
Can an unprivileged attacker front-run HinkalFactoryDeployer's SAFE_SINGLETON_FACTORY create2 with a matching salt to squat the address, to hijack the deterministic Hinkal address, deploy attacker bytecode at it, or permanently block the intended deployment, specifically when a prior tx in the same block left the action or tree in a partial state (where cross-tx residual state carries over)?

## Target
- File/function: contracts/HinkalFactory.sol :: deployHinkal / appendBytecodeChunk / HinkalFactoryDeployer
- Entrypoint: HinkalFactoryDeployer constructor / HinkalFactory (pre-ownership)
- Attacker controls: create2 salt via SAFE_SINGLETON_FACTORY, deployment ordering (only if reachable pre-owner)
- Exploit idea: race or corrupt the deterministic deployment before ownership is settled
- Invariant to test: the code at the deterministic Hinkal address == the audited Hinkal bytecode
- Expected Immunefi impact: Critical: permanent freezing of user funds
- Fast validation: Foundry: simulate the create2 race/hash mismatch, assert wrong code or blocked deploy
