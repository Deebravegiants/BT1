# Q5180: Min-circuit Emporium executor -> an ERC20 transfer moving tokens Emporium [when the external action is Em]

## Question
Can an unprivileged attacker set externalActionId == HINKAL_EMPORIUM_ACTION_ID with erc20TokenAddresses.length == 0 so formInputForCircom selects formInputEmporiumMin (proving only message == Poseidon(messageSeed)), then supply an EmporiumStack with signerAddress == 0 whose op performs an ERC20 transfer moving tokens Emporium holds to the attacker, while the balance loop iterates an empty token list and accounts for nothing, specifically when the external action is Emporium with signerAddress zero (where the unsigned stateless op path runs)?

## Target
- File/function: contracts/CircomDataBuilder.sol :: formInputForCircom / formInputEmporiumMin / EmporiumUpgradeable.runAction
- Entrypoint: Hinkal.transact (Emporium min path)
- Attacker controls: externalActionData.externalActionMetadata (EmporiumStack), emporiumMessage, empty token array
- Exploit idea: use the near-empty Min proof to run arbitrary ops from Emporium's identity with no accounting
- Invariant to test: assets Emporium can move in a tx == assets accounted in balancesBefore/balancesAfter
- Expected Immunefi impact: Critical: direct theft of shielded or in-flight user funds
- Fast validation: Foundry: fund Emporium, run min-path op stealing that balance, assert attacker gain
