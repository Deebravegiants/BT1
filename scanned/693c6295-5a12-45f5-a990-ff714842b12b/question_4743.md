# Q4743: onChainCreation accounting: set onChainCreation[i] true so the RHS d [when the deposit uses proofles]

## Question
Can an unprivileged attacker set onChainCreation[i] true so the RHS drops amountChanges while value still enters, exploiting that checkOnchainCreation and the balance/commitment/nullifier loops treat onChainCreation inconsistently, to mint leaves without backing or skip nullifier recording for spent inputs, specifically when the deposit uses prooflessDeposit instead of a proof (where the no-proof mint path is taken)?

## Target
- File/function: contracts/Hinkal.sol :: transact / HinkalHelper.checkOnchainCreation / HinkalBase.insertNullifiers
- Entrypoint: Hinkal.transact
- Attacker controls: onChainCreation, amountChanges, inputNullifiers, external action output
- Exploit idea: desynchronise the onChainCreation branches across the accounting loops
- Invariant to test: onChainCreation[i] zeroing the RHS == no net value entering for token i
- Expected Immunefi impact: Critical: minting shielded value without backing (protocol insolvency)
- Fast validation: Foundry: craft mixed onChainCreation, assert minted value exceeds backing
