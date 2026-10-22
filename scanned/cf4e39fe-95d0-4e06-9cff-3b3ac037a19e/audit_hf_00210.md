# [M] `LPToken.set_minter`

## Summary
Severity: Medium
Contest weight: 0.0253
Dataset id: 1097
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in a token contract that manages liquidity provider (LP) shares. The contract offers a function to update the privileged minter role, but it fails to verify that the supplied address is non‑zero before storing it. As a result, an actor who can call the update function can set the minter to the zero address (0x0000000000000000000000000000000000000000). This oversight occurs because the function lacks a basic input validation check, a common pattern for protecting against null addresses in Solidity. If the minter is set to the zero address, any subsequent minting operation that requires the minter role will either revert (if the contract checks for a valid minter) or silently succeed without actually crediting new tokens, effectively disabling the creation of new LP tokens. Users who provide liquidity expect to receive newly minted LP tokens that represent their share of the pool; when minting is disabled, they may see no increase in their LP balance, experience missing rewards, or encounter a frozen pool where no new shares can be issued. The impact is a denial‑of‑service condition for the token's core accounting mechanism, potentially freezing user funds and undermining trust in the protocol. This flaw was discovered during a formal audit where the reviewers examined privileged role‑management functions and noted the absence of a zero‑address guard. The issue can be subtle because assigning the zero address is syntactically valid, and the contract does not emit any warning or revert, making the bug easy to overlook in testing. To remediate, the setter should include a require statement that rejects a zero address before updating the minter storage slot, thereby preserving the invariant that a valid account must control token minting. In broader terms, this is an instance of missing input validation leading to a null‑address assignment defect, which can break role‑based access control and cause critical business logic failures such as funds disappearing from the expected minting flow.

## Recommendation
Check that `_minter` doesn’t equal zero before setting it as the new minter.
