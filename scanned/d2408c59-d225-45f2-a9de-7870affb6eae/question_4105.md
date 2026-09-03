# Q4105: Min-circuit Emporium executor -> a call into another external action whos [when onChainCreation[i] is tru]

## Question
Can an unprivileged attacker set externalActionId == HINKAL_EMPORIUM_ACTION_ID with erc20TokenAddresses.length == 0 so formInputForCircom selects formInputEmporiumMin (proving only message == Poseidon(messageSeed)), then supply an EmporiumStack with signerAddress == 0 whose op performs a call into another external action whose onlyAllowedRecipient trusts Emporium, while the balance loop iterates an empty token list and accounts for nothing, specifically when onChainCreation[i] is true for the affected token (where the RHS of the balance equation drops the amount term)?

## Target
- File/function: contracts/CircomDataBuilder.sol :: formInputForCircom / formInputEmporiumMin / EmporiumUpgradeable.runAction
- Entrypoint: Hinkal.transact (Emporium min path)
- Attacker controls: externalActionData.externalActionMetadata (EmporiumStack), emporiumMessage, empty token array
- Exploit idea: use the near-empty Min proof to run arbitrary ops from Emporium's identity with no accounting
- Invariant to test: assets Emporium can move in a tx == assets accounted in balancesBefore/balancesAfter
- Expected Immunefi impact: Critical: direct theft of shielded or in-flight user funds
- Fast validation: Foundry: fund Emporium, run min-path op stealing that balance, assert attacker gain
