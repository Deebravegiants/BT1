# [M] M-05 Unmitigated

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-04-ai-arena-mitigation
Published: 2024-04-16
Source: https://github.com/code-423n4/2024-04-ai-arena-mitigation-findings/issues/50
Type: code-finding

## Details
# Lines of code




# Vulnerability details

Mitigation of M-05: NOT mitigated, with error, see comments

https://github.com/ArenaX-Labs/2024-02-ai-arena-mitigation/blob/d81beee0df9c5465fe3ae954ce41300a9dd60b7f/src/FighterFarm.sol#L574

## Mitigated issue(s)
[M-05: Can mint NFT with the desired attributes by reverting transaction](https://github.com/code-423n4/2024-02-ai-arena-findings/issues/376)
(Also see duplicated reports [#1017](https://github.com/code-423n4/2024-02-ai-arena-findings/issues/1017), [#578](https://github.com/code-423n4/2024-02-ai-arena-findings/issues/578), [#1991](https://github.com/code-423n4/2024-02-ai-arena-findings/issues/1991))

There were four issues with the randomness of the DNA in FighterFarm.sol:
1. The user can retry the DNA set in `_createNewFighter()` by reverting the `onERC721Received()` hook.
2. The user can brute force his `msg.sender` which seeds the DNA in `reRoll()` and `claimFighters()`.
3. The user can wait for an appropriate `fighters.length` which seeds the DNA in `mintFromMergingPool()` and `claimFighters()`.
4. The user can select the best out of all rerolls, which can be calculated in advance.

(The issue of freely setting DNA in `mintFromMergingPool()` is part of [H-03: Players have complete freedom to customize the fighter NFT when calling redeemMintPass and can redeem fighters of types Dendroid and with rare attributes](https://github.com/code-423n4/2024-02-ai-arena-findings/issues/366).)

Additionally, a mitigation of [#578](https://github.com/code-423n4/2024-02-ai-arena-findings/issues/578), which was duplicated to [M-05 (#376)](https://github.com/code-423n4/2024-02-ai-arena-findings/issues/376), has been attempted. This issue was about the DNA simply being differently generated, due to a likely mistake, but with low impact.

[M-05: Can mint NFT with the desired attributes by reverting transaction](https://github.com/code-423n4/2024-02-ai-arena-findings/issues/376) is only 1. above, and I consider the other issues (including #578) to have been incorrectly or misleadingly duplicated to M-05, and I have to deal with them as separate/new issues/errors.
I have submitted reports on 2-4 as three new issues, as well as a report on the error from the mitigation of #578. I will make use of this submission as the report of an unmitigated 1., the details on which and recommended mitigation steps follow at the end of this report, after an overview of the review of these issues and the error.
The mitigation review of the part of the scope which is "M-05" thus consists of a total of 5 reports:
1. This report.
2. "User influence on DNA in `claimFighters()` (unmitigated issue 2. grouped under M-05)"
3. "User influence on DNA via `fighters.length` in `mintFromMergingPool()` (unmitigated issue 3. grouped under M-05)"
4. "The user can select the best out of all rerolls (unmitigated issue 4. grouped under M-05)"

   Error. "[M-05/#578] Mitigation error: user influence on DNA via `to`"

## Mitigation re- and overview
1. Nothing has been done to mitigate this.

2. has been mitigated in `reRoll()` by [replacing `msg.sender` with `tokenId`](https://github.com/ArenaX-Labs/2024-02-ai-arena-mitigation/blob/d81beee0df9c5465fe3ae954ce41300a9dd60b7f/src/FighterFarm.sol#L424). But [it has NOT been mitigated in `claimFighters()`](https://github.com/ArenaX-Labs/2024-02-ai-arena-mitigation/blob/d81beee0df9c5465fe3ae954ce41300a9dd60b7f/src/FighterFarm.sol#L241).

3. [Nothing has been done about this in `mintFromMergingPool()`](https://github.com/ArenaX-Labs/2024-02-ai-arena-mitigation/blob/d81beee0df9c5465fe3ae954ce41300a9dd60b7f/src/FighterFarm.sol#L366).
In `claimFighters()` `fighters.length` has been replaced by `nftsClaimed[msg.sender][0], nftsClaimed[msg.sender][1]`. This is only slightly better. `fighters.length` will be updated by all other users so the attacker would get a steady stream of new values. `nftsClaimed[msg.sender][]` is changed only by the user. However, by transferring the token to another address this value will change, so the user can still influence the DNA.

4. Nothing has been done to mitigate this.

In summary, none of the issues 1-4 have been fully mitigated.

#578 lead to replacing `msg.sender` by `to`. This introduced the error discussed below, also reported separately.

### Mitigation error - introduction of issue 2. in `mintFromMergingPool()`
In the mitigation of #578, having changed the DNA in `mintFromMergingPool()` from `uint256(keccak256(abi.encode(msg.sender, fighters.length)))` to [`uint256(keccak256(abi.encode(to, fighters.length)))`](https://github.com/ArenaX-Labs/2024-02-ai-arena-mitigation/blob/d81beee0df9c5465fe3ae954ce41300a9dd60b7f/src/FighterFarm.sol#L366) has introduced issue 2. for this function as well. `to` is [set to `msg.sender` from `MergingPool.claimRewards()`](https://github.com/ArenaX-Labs/2024-02-ai-arena-mitigation/blob/d81beee0df9c5465fe3ae954ce41300a9dd60b7f/src/MergingPool.sol#L163). This is checked to be a winner, which is [set by the admin in `pickWinners()` as the owner of the token](https://github.com/ArenaX-Labs/2024-02-ai-arena-mitigation/blob/d81beee0df9c5465fe3ae954ce41300a9dd60b7f/src/MergingPool.sol#L128). The user can transfer his token to an appropriate address, such that if he is picked as the winner this address generates the desired DNA. A complication for the user is that `fighters.length` might change, so he needs to take the few possible such values into account, and try to limit them by acting quickly and hoping not many fighters will be minted in between. In any case he can significantly influence his DNA.

### Overview of mitigation steps for 1-4 and the error
1. Do not set the DNA in the same transaction as the user receives the fighter.
2. Do not use `msg.sender` to set the DNA.
3. Do not use `fighters.length` to set the DNA.
4. Do not use currently known values to set the DNA.

    Error: Do not use `to` (here equivalent to `msg.sender` in 2.) to set the DNA.

If a third party decentralized VRF is not an option, you can act as your own centralized randomness provider, otherwise equivalent to the typical VRF oracles. The only consideration then is whether users will trust that your server is unbiased and uninfluenceable.
Otherwise it seems the best solution is to set the DNA as `blockhash(block.number - 1)` in a call from the admin, and then in a second call by the user assign the fighter to the user, whether this is by direct minting to the user, by transferring the fighter from an escrow (e.g. FighterFarm itself), or as a finalizing of the reroll.

## M-05: Can mint NFT with the desired attributes by reverting transaction
To clarify the original report:
This issue makes no claim about the direct influence of the DNA calculated in `_createNewFighter()`. The DNA is set in the same transaction as the the fighter is minted. The issue is that the user can let the DNA be calculated and the fighter minted to him, and then, based on what he is to receive, revert the transaction. This is enabled by the `onERC721Received()` hook.
`_createNewFighter()` calls [`_safeMint(to, newId)`](https://github.com/ArenaX-Labs/2024-02-ai-arena-mitigation/blob/d81beee0df9c5465fe3ae954ce41300a9dd60b7f/src/FighterFarm.sol#L574). This calls [`ERC721Utils.checkOnERC721Received(_msgSender(), address(0), to, newId, "")`](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/11dc5e3809ebe07d5405fe524385cbe4f890a08b/contracts/token/ERC721/ERC721.sol#L314), which on a contract executes
```solidity
try IERC721Receiver(to).onERC721Received(msg.sender, address(0), newId, "") returns (bytes4 retval) {
    if (retval != IERC721Receiver.onERC721Received.selector) {
        // Token rejected
        revert IERC721Errors.ERC721InvalidReceiver(to);
    }
```
The user (his contract) may thus implement his `onERC721Received()` to reject unwanted fighters, e.g.
```solidity
function onERC721Received(
    address operator,
    address from,
    uint256 tokenId,
    bytes calldata data
) public returns (bytes4){
    
    (,,uint256 weight,,,,) = fighterFarm.getAllFighterInfo(tokenId);
    require(weight == 95, "I don't want this attribute");

    return bytes4(keccak256(bytes("onERC721Received(address,address,uint256,bytes)")));
}
```

### Recommended mitigation steps
There is no way to avoid this issue if the randomness is set in the same transaction as the minting/`onERC721Received()` call. The DNA must be committed first, and then, in a separate transaction, should the user be able to get his fighter. One way is to mint the fighter to the FighterFarm contract, acting as an escrow, and implementing a function for the user to claim it by having it transferred to him.
