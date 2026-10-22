# [M] BondNFTs can revert when transferred

## Summary
Severity: Medium
Contest weight: 0.8129
Dataset id: 17353
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
`BondNFT`s should be transferrable. According the the proposal and the sponsor, `BondNFT`s should could be sold and borrowed against.

The proposal for context: <https://gov.tigris.trade/#/proposal/0x2f2d1d63060a4a2f2718ebf86250056d40380dc7162fb4bf5e5c0b5bee49a6f3>

The current implementation limits selling/depositing to only the same day that rewards are distributed for the `tigAsset` of the bond.

The impact if no rewards are distributed in the same day:

  1. `BondNFT`s listed on open markets will not be able to fulfill the orders
  2. `BondNFT`s deposited as collateral will not be able to release the collateral

Because other market/platforms used for selling/depositing will not call `claimGovFees` to distribute rewards, they will revert when trying to transfer the `BondNFT`.

Realistic examples could be `BondNFT`s listed on OpenSea.

Example of reasons why rewards would not be distributed in the same day:

  1. Low activity from investors, rewards are distributed when users lock/release/extend
  2. `tigAsset` is blacklisted in `BondNFT`, rewards will not be distributed in such case.

## Proof of Concept
`BondNFT` has a mechanism to update the time `tigAsset` rewards are distributed. It uses a map that points to the last timestamp rewards were distributed for `epoch[tigAsset]`.

`distribute` function in `BondNFT`:

```solidity
function distribute(
    address _tigAsset,
    uint _amount
) external {
    if (totalShares[_tigAsset] == 0 || !allowedAsset[_tigAsset]) return;
    IERC20(_tigAsset).transferFrom(_msgSender(), address(this), _amount);
    unchecked {
        uint aEpoch = block.timestamp / DAY;
        if (aEpoch > epoch[_tigAsset]) {
            for (uint i=epoch[_tigAsset]; i<aEpoch; i++) {
                epoch[_tigAsset] += 1;
                accRewardsPerShare[_tigAsset][i+1] = accRewardsPerShare[_tigAsset][i];
            }
        }
        accRewardsPerShare[_tigAsset][aEpoch] += _amount * 1e18 / totalShares[_tigAsset];
    }
    emit Distribution(_tigAsset, _amount);
}
```

(Please note that if the asset is blacklisted through `allowedAsset`, the `epoch[tigAsset]` will not be updated)

When `BondNFT`s are transferred, a check is implemented to make sure `epoch[tigAsset]` is updated to the current day.

According to the sponsor, the reason for this check is to make sure that a bond that should be expired doesn’t get transferred while the epoch hasn’t yet been updated.

`_transfer` function in `BondNFT`: <https://github.com/code-423n4/2022-12-tigris/blob/588c84b7bb354d20cbca6034544c4faa46e6a80e/contracts/BondNFT.sol#L329>

```solidity
function _transfer(
    address from,
    address to,
    uint256 _id
) internal override {
    Bond memory bond = idToBond(_id);
    require(epoch[bond.asset] == block.timestamp/DAY, "Bad epoch");
    require(!bond.expired, "Expired!");
    unchecked {
        require(block.timestamp > bond.mintTime + 300, "Recent update");
        userDebt[from][bond.asset] += bond.pending;
        bondPaid[_id][bond.asset] += bond.pending;
    }
    super._transfer(from, to, _id);
}
```

As can be seen above, if `epoch[tigAsset]` is not set to the same day of the transfer, the transfer will fail and the impacts in the impact section will happen.

## Recommendation
The reason for the check is to validate that a bond.expired updated according to the actual timestamp.

Instead of having

```solidity
require(epoch[bond.asset] == block.timestamp/DAY, "Bad epoch");
require(!bond.expired, "Expired!");
```

You could replace it with:

```solidity
require(bond.expireEpoch >= block.timestamp/DAY, "Transfer after expired not allowed");
```

The warden has shown a way for the BondNFT to not be transferable, because this shows a functionality loss, given a specific circumstance, I agree with Medium Severity.

**[GainsGoblin (Tigris Trade) resolved](https://github.com/code-423n4/2022-12-tigris-findings/issues/162#issuecomment-1407489822):**

Mitigation: <https://github.com/code-423n4/2022-12-tigris/pull/2#issuecomment-1419174264>
