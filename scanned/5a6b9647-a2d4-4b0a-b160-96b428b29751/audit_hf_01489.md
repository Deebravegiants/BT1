# [H] H-3 An intruder can block any users

## Summary
Severity: High
Contest weight: 0.0748
Dataset id: 7923
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in the mint function of the FantiumMinterV1 contract, which accepts an arbitrary destination address parameter (_to) without performing any validation or access‑control checks. Because the function proceeds to modify the permit state of the supplied address after the minting logic, an attacker who can invoke mint can supply the address of any legitimate user and cause the contract to alter that user’s permit, effectively revoking or changing their allow‑list status. This flaw originates from a missing validation step that should ensure only authorized recipients (for example, the platform manager or a pre‑approved list) can be passed to mint, and from conflating token minting with permission management in a single routine. Exploitation is straightforward: the attacker calls mint with the victim’s address as _to, the contract mints tokens (or performs a no‑op) and then updates the victim’s permit entry, causing the victim to be blocked from future protocol actions such as deposits, withdrawals, or further minting. The impact is that any user on the platform can be arbitrarily disabled, leading to loss of access to funds, inability to interact with the protocol, and potential financial loss if the blocked user cannot retrieve deposited assets. The condition for the attack is simply the ability to call the public mint function; no special role or permission is required because the function does not restrict callers. All users, especially those relying on the allow‑list for participation, are affected. The issue was uncovered during a manual security audit that examined the flow of data through mint and identified that the _to argument was never checked before being used to modify permission state. Because the mint function appears benign and the permission change is hidden behind a standard token‑minting call, the bug can be hard to notice without a deep code review. To remediate, the contract should separate minting from permission updates, enforce strict validation of the _to address (e.g., require it to be the caller, a platform manager, or an address on an approved list), and restrict any permit‑changing logic to callers with the onlyPlatformManager role. This aligns the implementation with the intended business logic that only authorized entities can alter user permissions, preventing arbitrary blocking of users.

## Recommendation
We recommend that you rethink the logic of allowList.
