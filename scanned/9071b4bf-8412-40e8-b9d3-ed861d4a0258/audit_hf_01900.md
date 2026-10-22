# [M] NFT breeding cooldown is calculated wrong

## Summary
Severity: Medium
Contest weight: 0.5753
Dataset id: 10484
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The protocol lets users breed their NFTs. Two NFTs can only be bred together if their cooldownEndBlock
is less than block.number as seen below:
```solidity
function _isReadyToBreed(NFT storage nft) internal view returns (bool) {
    return (nft.siringWithId == 0) && (nft.cooldownEndBlock <=
        block.number);
}
```
Additionally, an NFT only gives birth if the same cooldown is less than block.number - enforced by the
_isReadyToGiveBirth function.
The problem is how this cooldown is calculated. Taking a look at the only function that it is updated in we
can see that it actually calculates the block that would end the cooldown.
```solidity
function _triggerCooldown(NFT storage _nft) internal { // ok
    _nft.cooldownEndBlock = uint64(
        (cooldowns[_nft.generation] / secondsPerBlock) + block.number
    );
}
```
The problem here, however, is that secondsPerBlock is set 15, while the average block time on the Pume
Network is ~0.5 seconds (This can be verified on the plume testnet's official website: https://plume-
testnet.explorer.caldera.xyz/ ). Having in mind the secondsPerBlock is set to 15 which is around 30 times
more than the network block time this completely breaks the NFT cooldown logic. Also, it is bad in general
to use block.number for time tracking operations as it is certainly NOT constant. Block time may be 0.4
seconds causing the cooldowns to pass faster or 0.6 seconds (if there is less activity) causing cooldown
times to pass slower.

## Recommendation
The most robust solution would be to use block.timestamp instead of blocks to track the NFT cooldown.
