# [H] An attacker is able to hijack any rented ERC1155 tokens and brick rentals involving ERC1155 tokens

## Summary
Severity: High
Chain: Smart contract
Component: 2024-02-renft-mitigation
Published: 2024-03-04
Source: https://github.com/code-423n4/2024-02-renft-mitigation-findings/issues/27
Type: code-finding

## Details
# Lines of code

https://github.com/re-nft/smart-contracts/blob/97e5753e5398da65d3d26735e9d6439c757720f5/src/modules/Storage.sol#L1


# Vulnerability details


# Impact

An attacker can hijack any rented ERC1155 tokens and therefore permanently brick rentals involving ERC1155 tokens.


# The vulnerability

For this vulnerability to be exploited, an attacker needs to create a malicious order where the lender is a malicious smart contract the attacker controls and the borrower is also himself, so it's a self-lend. This self-lend takes advantage of a reentrancy during it's termination ([`Stop::stopRent(maliciousOrder)`]) allowing an attacker to hijack the ERC1155 tokens. 

## Proof of concept scenario

1. The attacker borrows 100 APE ERC1155 tokens with ID 5, from Alice
    - When the rental is added to the `Storage` through the function [`Storage::addRentals()`](https://github.com/re-nft/smart-contracts/blob/97e5753e5398da65d3d26735e9d6439c757720f5/src/modules/Storage.sol#L220), the state variable mapping `rentedAssets` is updated with how much ERC1155 tokens has the borrower (in this case, the attacker) has borrowed. 
    - So calling `Storage.isRentedOut(attackerRentalSafe, APE_ERC1155, 5)` will return `100`, since that's the amount of APE ERC1155 tokens the attacker has borrowed so far.
    - Also calling `APE_ERC1155.balanceOf(attackerRentalSafe, 5)` will also return `100`, since that's the amount of APE ERC1155 tokens with ID 5 the attacker has in his rental safe

2. The attacker creates a malicious smart contract with a malicious `onERC1155Received` callback function (more on what it'll do later).

3. The attacker owns 100 APE ERC1155 (other than the ones borrowed, these are just ones he owned before borrowing), he will transfer them to the malicious smart contract he created

4. The attacker creates a malicious `PAY` rental order (`BASE` also works), sets the offerer (lender) of the order to be the malicious smart contract, sets two offer items:      

    - 1st offer item would be `1x` APE ERC1155 tokens with ID 5
    - 2nd offer item would be `99x` APE ERC1155 tokens with ID 5

5. The attacker will fulfill that malicious order using his rental safe. So at this point, the lender would be the malicious attacker-controlled smart contract and the fulfiller would be the attacker's rental safe holding the 100 APE tokens borrowed from Alice

6. The malicious rental will begin execution, the (1 + 99) APE tokens in the malicious smart contract will be transferred to the attacker's rental safe and the rental will be stored in the `Storage.sol`. At this point:
    - Calling `Storage.isRentedOut(attackerRentalSafe, APE_ERC1155, 5)` will return `200`, since that's the amount of APE ERC1155 tokens with ID 5 the attacker has borrowed so far (100 from Alice + 100 from himself)
    - Calling `APE_ERC1155.balanceOf(attackerRentalSafe, 5)` will also return `200`, since that's the amount of APE ERC1155 tokens with ID 5 the attacker has in his rental safe

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-02-renft-mitigation-findings/issues/27_
