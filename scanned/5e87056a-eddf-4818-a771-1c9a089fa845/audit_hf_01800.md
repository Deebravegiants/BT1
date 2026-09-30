# [H] Accountant can’t be initialized

## Summary
Severity: High
Contest weight: 0.6403
Dataset id: 9973
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is an initialization failure in the Accountant module of the lending market protocol. During the AccountantDelegate.initialize call, the contract asserts that the accountant’s token balance equals the accountant’s initial supply by using the condition `require(note.balanceOf(msg.sender) == note.totalSupply(), "AccountantDelegate::initialize: Accountant has not received payment")`. However, the `_initialSupply` variable that the require statement indirectly checks is hard‑coded to 0 in the ERC20 constructor and never updated after the massive mint to the accountant (`type(uint).max` tokens). Consequently, the accountant’s balance will always be non‑zero while the recorded initial supply remains zero, causing the require to revert every time initialize is invoked. This logical mismatch prevents the accountant contract from ever being set up, meaning that any downstream functionality that relies on the accountant – such as fee collection, accounting of loans, or protocol governance that depends on the accountant’s state – remains inaccessible. The impact is that the protocol cannot perform essential bookkeeping, potentially leading to funds being locked or the market being unusable for lenders and borrowers. The condition is triggered whenever the deployment script attempts to call the initialize function after minting tokens, which is part of the normal launch process, so the bug manifests at contract deployment time. All participants—protocol operators, users depositing collateral, and anyone expecting the accountant to process payments—are affected because the expected accounting layer never becomes active. The issue was discovered during a formal security audit when the auditors examined the initialization flow and noticed that the require statement compared the accountant’s balance against a value that never changes from zero. The bug is subtle because the require looks reasonable; it checks that the accountant “has received payment,” but the variable used does not reflect the actual token supply after minting, making the check silently always fail. To remediate, the require should compare the accountant’s balance with the token’s totalSupply (or another variable that reflects the minted amount) instead of the immutable `_initialSupply`. This change restores the intended logic, allowing the accountant to initialize correctly, enabling the protocol’s accounting mechanisms to function as designed. The defect belongs to the class of incorrect initialization checks or misuse of immutable state variables, where an invariant is enforced against a stale or unrelated value, breaking contract bootstrapping and leading to missing or frozen functionality.

## Proof of Concept
The issue is the following `require()` statement: <https://github.com/Plex-Engineer/lending-market/blob/main/contracts/Accountant/AccountantDelegate.sol#L29>

There, the function checks whether the accountant has received the correct amount of tokens. But, it compares the accountant’s balance with the `_initialSupply`. That value is always 0. So the require statement will always fail

When the Note contract is initialized, `_initialSupply` is set to 0:

  * <https://github.com/Plex-Engineer/lending-market/blob/main/deploy/canto/004_deploy_Note.ts#L14>
  * <https://github.com/Plex-Engineer/lending-market/blob/main/contracts/Note.sol#L9>
  * <https://github.com/Plex-Engineer/lending-market/blob/main/contracts/ERC20.sol#L32>

After `_mint_to_Accountant()` mints `type(uint).max` tokens to the accountant: <https://github.com/Plex-Engineer/lending-market/blob/main/contracts/Note.sol#L18>  
That increases the `totalSupply` but not the `_initialSupply`: <https://github.com/Plex-Engineer/lending-market/blob/main/contracts/ERC20.sol#L242>

The `_initialSupply` value is only modified by the ERC20 contract’s constructor.

## Recommendation
Change the require statement to

```solidity
require(note.balanceOf(msg.sender) == note.totalSupply(), "AccountantDelegate::initiatlize: Accountant has not received payment");
```

The warden has shown how, due to an incorrect assumption, `AccountantDelegate.initialize` cannot work, meaning part of the protocol will never work without fixing this issue.

While the change should be fairly trivial, the impact is pretty high, for those reasons am going to raise severity to High.
