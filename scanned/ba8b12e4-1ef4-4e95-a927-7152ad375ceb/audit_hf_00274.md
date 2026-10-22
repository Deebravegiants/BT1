# [M] All the scxMinted is at risk of being burnt.

## Summary
Severity: Medium
Contest weight: 0.4138
Dataset id: 1396
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
If one of the variables that calculate adjustedRectangle is a zero value, it will impair the calculation of excessSCX which would equal to all of the scxMinted on line 219. Nothing will be deducted from scxMinted on line 229 since adjustedRectangle = 0 putting all of the former at risk of being burnt(line 230).

Also, the check on line 224 would not pass for high value migrations since scxMinted would always be greater than the adjustedRectangle. No scx would be avaliable to be sent to the AMM helper nor would there be any LP minted.

Furthermore, since SCX is needed to ensure the proper functioning of the protocol, ie, to provide liquidity and influence the value of Flan, it would be imperative that the correct value of excessScx is accounted for.

## Recommendation
Insert a require statement on line 222:

```solidity
require(adjustedRectangle != 0, "err");
```

I really appreciate how deeply you’ve thought about this. Requires a thorough understanding of Limbo. Indeed your handle is apt (unless you’re just naming yourself after the marvel hero in which case I would have to see your archery skills).

The RectangleOfFairness is hardcoded as a constant 30 eth in Limbo.sol (line 269) so that can’t be zero. The only way it could be zero is if the inflation factor is zero which is a community set variable. However, there might be some funny community edge case where they want it set to zero. For instance, suppose the community feels in some distant future that flan is sufficiently liquid but that SCX is still a bit dilute. Maybe they’d want to bring on new tokens while burning all new scx.

I’m marking this as acknowledged, rather than disputed because your reasoning is really good.
