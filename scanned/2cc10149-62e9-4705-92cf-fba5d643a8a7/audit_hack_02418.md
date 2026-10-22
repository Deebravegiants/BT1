# [H] Unexpected value for MAX\_TOKENS\_SOLD

## Summary
Severity: High
Source: https://github.com/kikinteractive/kin-token/blob/3ed3a383b9304274ec22f41769716cadb854727f/contracts/KinTokenSale.sol#L33
Type: audit-issue

## Details
The state variable [MAX\_TOKENS\_SOLD](https://github.com/kikinteractive/kin-token/blob/3ed3a383b9304274ec22f41769716cadb854727f/contracts/KinTokenSale.sol#L33) in `KinTokenSale` represents the maximum number of tokens to be sold during the crowdsale, which is defined to be 1 trillion according to the [whitepaper](https://kin.kik.com/papers/Kin%5FWhitepaper%5FV1%5FEnglish.pdf) (chapter 6, Kin token issuance). However, the value in the contract is 512192121951 (slightly above half a trillion). Update this constant to reflect the value indicated in the whitepaper.

_**Update:** The team pointed out that this number represents the amount that will be offered during the sale, while the remaining half of the 1 trillion offered to the public [has been sold in a presale](https://medium.com/kinfoundation/kin-tde-if-you-want-to-participate-you-must-register-by-september-9-9-00-a-m-et-2f1304a4aa4b)_.\_
