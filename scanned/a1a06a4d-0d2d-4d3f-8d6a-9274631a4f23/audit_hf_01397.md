# [M] Denial of Service due to Business Logic Flaw (Authenticated)

## Summary
Severity: Medium
Contest weight: 0.1532
Dataset id: 7166
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a user connects their wallet to dedprz.virtual.tech, the application does not adequately handle the scenario where the user might accidentally or intentionally press the withdraw button as their first interaction. When this happens, all remaining options/buttons become locked, except for the “Get $USA to Play” button. While this functionality may be convenient during an ongoing game, it creates the impression that the entire application is frozen if it occurs during the user’s initial interaction. Although refreshing the page resolves the issue, this situation effectively results in a form of Denial of Service (DoS), as there is no in-app mechanism for recovery.

## Proof of Concept
With the connected wallet, navigate to dedprz.virtual.tech and hit the Withdraw button. After it, the remaining functionality is completely frozen and the user is unable to start a game until it refreshes the page.

## Recommendation
Please revise the application’s business logic to ensure that if the user presses the withdraw button at an early stage, the UI and browsing experience are not locked without a clear reason, and the user can recover without the need of refreshing the page.
