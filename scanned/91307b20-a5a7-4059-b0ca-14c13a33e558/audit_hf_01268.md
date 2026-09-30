# [H] Unrestricted Username Registration and Sybil Attack Risk

## Summary
Severity: High
Contest weight: 0.6116
Dataset id: 5881
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The registerPlayer function in the contract does not enforce unique registrations per msg.sender, allowing an attacker to register multiple usernames with the same address. This causes several problems:
1. Username Sniping & Frontrunning: A malicious actor can preemptively register desirable usernames before legitimate users can do so, blocking access to those names.
2. Spam Registration: Without restrictions, the attacker can flood the system with numerous registrations, preventing others from acquiring common or desirable usernames.
3. Referral Farming: If referral-based incentives exist, an attacker could exploit the lack of controls to generate multiple accounts and extract undue rewards.
4. Lack of Age Verification: The function does not validate the isOldEnough parameter, allowing ineligible users to register without restrictions.

## Proof of Concept
```solidity
function testRegisterPlayerSameSenderAndSameUsername() public {
    // Allowed from the same msg.sender
    vm.startPrank(attacker);
    riskiit.registerPlayer("alice", true, "");
    riskiit.registerPlayer("bob", true, "");
    riskiit.registerPlayer("charlie", true, "");
    vm.stopPrank();
    // Will revert
    vm.prank(alice);
    riskiit.registerPlayer("alice", true, "");
}
```

## Recommendation
To mitigate these issues, the contract should enforce strict validation for username uniqueness per msg.sender. Implementing a backend-signed verification mechanism can help ensure each username is registered only by its rightful owner while preventing automated spam registrations.
Additionally, age verification should be cryptographically validated rather than relying on an unchecked boolean input.
