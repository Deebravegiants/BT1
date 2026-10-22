# [M] Compromise check will prevent

## Summary
Severity: Medium
Contest weight: 0.2455
Dataset id: 1808
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A missing compromise check in verifiedProfileIdForAddress will cause unauthorized access for affected contracts as compromised addresses can bypass security measures and perform malicious actions. (e.g: Attacker can steal user's private key, so address is compromised)
In EthosProfile.sol, the verifiedProfileIdForAddress function is missing a check to ensure _address is not compromised, allowing compromised addresses to interact with network/blob/979e352d7bcdba3d0665f11c0320041ce28d1b89/ethos/packages/contracts/contracts/EthosProfile.sol#L568-L574
The verifiedProfileIdForAddress function used in many contracts.
a3d0665f11c0320041ce28d1b89/ethos/packages/contracts/contracts/EthosAttestation
cdba3d0665f11c0320041ce28d1b89/ethos/packages/contracts/contracts/EthosDiscuss
52d7bcdba3d0665f11c0320041ce28d1b89/ethos/packages/contracts/contracts/EthosDiscussion.sol#L158-L160 ...
In this project, there are many issues about this compromised address. In almost contracts, it doesn't check msg.sender is compromised address. Address is already unregistered from profile by deleteAddressAtIndex function, but it is still used in many functions.
Internal pre-conditions
User needs to call deleteAddressAtIndex to set isAddressCompromised to be true for the target address.
External pre-conditions
Attack Path
1. Attack steal user's private key.
2. User detected it is compromised and calls deleteAddressAtIndex for marking isAddressCompromised as true for the target address.
3. Attacker can calls addReview in EthorsReview contract by compromised address. (private key is stolen so attacker can do this operation) It calls ethosProfile.verifiedProfileIdForAddress(msg.sender); msg.sender is compromised but it doesn't revert.
The protocol suffers a potential security breach as compromised addresses can bypass verification and execute unauthorized actions in dependent contracts, potentially leading to manipulation of contract functionality. The attacker gains access to otherwise restricted operations without proper authorization.

## Recommendation
Add modifier checkIfCompromised and use checkIsAddressCompromised function.
