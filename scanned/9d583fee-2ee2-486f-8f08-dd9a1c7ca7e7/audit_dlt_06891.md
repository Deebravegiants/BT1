# [M] All the scxMinted is at risk of being burnt.(Limbo.sol)

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-01-behodler
Published: 2022-02-02
Source: https://github.com/code-423n4/2022-01-behodler-findings/issues/335
Type: code-finding

## Details
# Handle

Hawkeye


# Vulnerability details

## Impact
If one of the variables that calculate adjustedRectangle is a zero value,it will impair the calculation of excessSCX which would equal to all of the scxMinted on line 219.Nothing will be deducted from scxMinted on line 229 since adjustedRectangle =0 putting all of the former at risk of being burnt(line 230).

Also, the check on line 224 would not pass for high value migrations since scxMinted would always be greater than the adjustedRectangle.No scx would be avaliable to be sent to the AMM helper nor would there be any LP minted.

Furthermore, since SCX is needed to ensure the proper functioning of the protocol,ie, to provide liquidity and influence the value of Flan, it would be imperative that the correct value of excessScx is accounted for.


## Tools Used
Manual Analysis 

## Recommended Mitigation Steps
Insert a require statement on line 222:

require (AdjustedRectangle! =0, “ err”)
