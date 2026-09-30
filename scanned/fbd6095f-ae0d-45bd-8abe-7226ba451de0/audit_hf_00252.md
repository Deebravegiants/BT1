# [M] `Basket:handleFees`

## Summary
Severity: Medium
Contest weight: 0.1978
Dataset id: 1291
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The fee calculation is based on the totalSupply of the basket token. But some amount of the totalSupply represents the fees paid to the publisher/ protocol owner. Therefore the fees are “overcharged”: because the fee amount is calculated on a part of already “paid” fees, should only take into account what is “owned” by the users and not the publisher/protocol owner.

## Proof of Concept
L141: the fee percent is multiplied by startSupply (=basket token total supply)  
L144 & L145: publisher / protocol owner receive basket tokens as fees payment  
[Basket.sol#L141](https://github.com/code-423n4/2021-12-defiprotocol/blob/205d3766044171e325df6a8bf2e79b37856eece1/contracts/contracts/Basket.sol#L141)

## Recommendation
* account the fee amount in a storage variable: uint256 feeAmount;
  * subtract feeAmount from startSupply L141: uint256 fee = (startSupply - feeAmount) * feePct / (BASE - feePct); // note the other bug about only dividing by BASE
  * add the fee to feeAmount after the calculation: feeAmount += fee;
  * if publisher/protocol owner burn basket token, reduce the feeAmount etc.

Generally we think that the amount of overcharged fees from this matter will be very negligible in the long term. It is worth noting that the fix proposed would not really solve the problem as not all tokens owned by the publisher/owner may be fees as well as they could just transfer those fees to another account and burn from there.

I’m not sure if this is correct. `startSupply` is indeed equal to `totalSupply()` but it is queried before new tokens are minted to the factory owner and publisher. As such, the fees appear to be correctly charged. I’ll have @frank-beard confirm this as I may have missed something.

Considering @frank-beard has not replied to this, I’m gonna make the final judgement and keep this open. I think it makes sense to track the fees paid out to the factory owner and publisher and have this amount excluded from the fee calculations. Upon either party burning tokens, this fee amount tracker must be updated accordingly. Due to the added complexity, it is understandable that this issue would be deemed a wontfix by the sponsor.

Yeah so I do agree that it does make sense generally to track the fees paid out and exclude, however in this case the impact is very low and yeah the complexity to deal with it doesn’t seem worth it.
