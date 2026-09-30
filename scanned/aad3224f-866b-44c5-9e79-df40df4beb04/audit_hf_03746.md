# [M] mintRollovers should require entitledShares

## Summary
Severity: Medium
Contest weight: 0.1278
Dataset id: 19900
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
mintRollovers should require entitledShares >= relayerFee
In mintRollovers, the rollover is only not skipped if queue[index].assets >= relayerFee,
if (entitledShares > queue[index].assets) {
// skip the rollover for the user if the assets cannot cover the relayer fee instead of revert.
if (queue[index].assets < relayerFee) {
index++;
continue;
}
In fact, since the user is already profitable, entitledShares is the number of assets of the user, which is greater than queue[index].assets, so it should check that entitledShares >= relayerFee, and use entitledShares instead of queue[index].assets to subtract relayerFee when calculating assetsToMint later.
This will prevent rollover even if the user has more assets than relayerFee

## Recommendation
Change to
if (entitledShares > queue[index].assets) {
// skip the rollover for the user if the assets cannot cover the relayer fee instead of revert.
- if (queue[index].assets < relayerFee) {
+ if (entitledShares < relayerFee) {
index++;
continue;
}
...
- uint256 assetsToMint = queue[index].assets - relayerFee;
+ uint256 assetsToMint = entitledShares - relayerFee;
