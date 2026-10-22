# [M] `OpenEdition.buy

## Summary
Severity: Medium
Contest weight: 0.5680
Dataset id: 17228
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The OpenEdition contract implements a public buy function that accepts an amount of tokens to purchase and validates that the caller sent exactly amount multiplied by the edition price. The function stores the requested amount in a uint24 variable and the price of the edition is stored as a uint72. The validation line performs amount * sale.price and relies on Solidity’s built‑in overflow checking (introduced in version 0.8) to revert if the multiplication overflows. Because the multiplication is evaluated in the uint72 domain, any combination where amount * sale.price exceeds the maximum value representable by a uint72 (2**72‑1) triggers an overflow, causing the require statement to revert with the generic "WRONG PRICE" error. This means that a perfectly valid purchase – for example buying 64 units when the price is 73 × 10¹⁸ wei – will fail even though the caller supplied the correct ether amount. The bug manifests only when the product of amount and price is large enough to overflow, which may not be obvious during normal testing with small values, making it hard to notice. From a user’s perspective the transaction simply reverts, the UI may display a generic price‑mismatch error, and the buyer receives no tokens despite sending the correct funds, effectively losing the opportunity to acquire the edition. The affected parties are any buyer attempting large‑scale purchases, the protocol that loses legitimate sales revenue, and any downstream services that assume the buy function always succeeds when the price is correct. The issue was discovered during a formal audit (Code4rena) where the overflow annotation was added to the require line. It belongs to the class of arithmetic overflow vulnerabilities that break business logic by violating the assumption that price × amount fits within the chosen integer type. To remediate the problem the multiplication should be performed in a wider type (e.g., uint256) or explicitly cast the operands before multiplication, and the require should compare the full‑precision product against msg.value, as shown in the recommended code snippet. This change eliminates the overflow check failure and restores the intended behavior where a correct payment always succeeds.

## Proof of Concept
`OpenEdition.buy()` validates the total funds like below.
```solidity
        function buy(uint256 _amount) external payable {
            uint24 amount = uint24(_amount);
            Sale memory temp = sale;
            IEscher721 nft = IEscher721(temp.edition);
            require(block.timestamp >= temp.startTime, "TOO SOON");
            require(block.timestamp < temp.endTime, "TOO LATE");
            require(amount * sale.price == msg.value, "WRONG PRICE"); //@audit overflow
```
Here, `amount` was declared as `uint24` and `sale.price` is `uint72`.

And it will revert when `amount * sale.price >= type(uint72).max` and such cases would be likely to happen e.g. `amount = 64(so 2^6), sale.price = 73 * 10^18(so 2^66)`.

As a result, `buy()` might revert when it should work properly.

## Recommendation
We should modify like below.
```solidity
        require(uint256(amount) * sale.price == msg.value, "WRONG PRICE");
```
