# Q1668: onChainCreation accounting: combine onChainCreation with an external [when the erc20TokenAddresses a]

## Question
Can an unprivileged attacker combine onChainCreation with an external action returning UTXOs for the same token, exploiting that checkOnchainCreation and the balance/commitment/nullifier loops treat onChainCreation inconsistently, to mint leaves without backing or skip nullifier recording for spent inputs, specifically when the erc20TokenAddresses array is reordered (where index-dependent loops behave differently)?

## Target
- File/function: contracts/Hinkal.sol :: transact / HinkalHelper.checkOnchainCreation / HinkalBase.insertNullifiers
- Entrypoint: Hinkal.transact
- Attacker controls: onChainCreation, amountChanges, inputNullifiers, external action output
- Exploit idea: desynchronise the onChainCreation branches across the accounting loops
- Invariant to test: onChainCreation[i] zeroing the RHS == no net value entering for token i
- Expected Immunefi impact: Critical: minting shielded value without backing (protocol insolvency)
- Fast validation: Foundry: craft mixed onChainCreation, assert minted value exceeds backing
