# [H] Anyone can deposit to DarkpoolAssetManager as the owner can be freely chosen without any implication

## Summary
Severity: High
Contest weight: 0.0575
Dataset id: 15195
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in the deposit functions of the asset manager contract, specifically depositETH() and depositERC20(). Both functions accept an address parameter that designates the owner of the deposited funds, but they do not enforce any relationship between this owner argument and the caller (msg.sender). As a result, any external account can invoke the functions and arbitrarily assign the deposit to any address while the caller still supplies the value and receives the corresponding receipt token. The root cause is the missing access‑control check or signature verification for the supplied owner field, allowing the owner to be freely chosen. An attacker can exploit this by calling the deposit function with a victim’s address as the owner, thereby crediting the victim’s internal balance while the attacker retains the external token or receipt. Later, if the protocol permits withdrawals based solely on the internal balance mapping, the attacker may be able to trigger a withdrawal on behalf of the victim or cause double‑spending by moving the same funds through multiple owner entries. The impact includes mis‑attribution of assets, potential loss of funds for honest users, corrupted accounting, and a breach of the protocol’s financial integrity. The condition under which the bug manifests is any execution of the deposit functions; there is no conditional guard that restricts the owner argument. All participants of the pool—depositors, token holders, and the protocol itself—are affected because the internal ledger can be polluted with false ownership records. The issue was discovered during a manual security audit performed by ThreeSigma, which flagged the owner parameter as unchecked. It can be hard to notice because the transaction appears to succeed, the UI may display the deposited amount for the chosen owner, and the contract does not emit an explicit warning about the mismatch between sender and owner. To remediate, the contract should either set the owner implicitly to msg.sender or require a cryptographic signature from the declared owner that proves consent, thereby binding the deposit to a verified party. This change restores the intended invariant that only the depositor can credit their own balance, preserving correct accounting and preventing unauthorized fund attribution.

## Recommendation
The owner should be the msg.sender or the owner signature should be validated (so it can be relayed).
