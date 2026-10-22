# [H] mint for 0 cost when the sale is over

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
# Handle

paulius.eth


# Vulnerability details

## Impact
function getPrice returns 0 when elapsed > saleDuration, it does not revert when the sale is over and function mint does not check that. So a 0 salePrice will be used to charge the msg.sender and make a useless transfer to the beneficiary. I am not sure if this was intended (free minting if the numSales limit is not reached during the sale duration).

## Recommended Mitigation Steps
Depends on the intentions but in my assumptions, mint should revert when the sale duration is over. I have marked this issue as low risk as I am really not sure about the intentions, no specification was provided.
