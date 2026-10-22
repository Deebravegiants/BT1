# [H] Loss of funds in `matchOneToManyOrders`

## Summary
Severity: High
Contest weight: 0.8497
Dataset id: 11647
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Function `matchOneToManyOrders()` and `takeOrders()` and `matchOrders()` suppose to match `sell order` to `buy order` and should perform some checks to ensure that user specified parameters in orders which are signed are not violated when order matching happens. but There is no check in their execution flow to check that an `order` has different `NFT token ids` in each one of it’s collections, so even so number of tokens could be valid in `order` to `order` transfer but the number of real transferred tokens and their IDs can be different than what user specified and signed. and user funds would be lost. (because of `ERC1155` there can be more than one token for a `tokenId`, so it would be possible to transfer it)

## Proof of Concept
This is `_takeOrders()` and `and` code:
```solidity
/**
 * @notice Internal helper function to take orders
 * @dev verifies whether order can be executed
 * @param makerOrder the maker order
 * @param takerItems nfts to be transferred
 * @param execPrice execution price
 */
function _takeOrders(
    OrderTypes.MakerOrder calldata makerOrder,
    OrderTypes.OrderItem[] calldata takerItems,
    uint256 execPrice
) internal {
    bytes32 makerOrderHash = _hash(makerOrder);
    bool makerOrderValid = isOrderValid(makerOrder, makerOrderHash);
    bool executionValid = IComplication(makerOrder.execParams[0]).canExecTakeOrder(makerOrder, takerItems);
    require(makerOrderValid && executionValid, 'order not verified');
    _execTakeOrders(makerOrderHash, makerOrder, takerItems, makerOrder.isSellOrder, execPrice);
}
```

As you can see it uses `canExecTakeOrder()` to check that it is valid to perform matching. This is `canExecTakeOrder()` and `areTakerNumItemsValid()` and `doTokenIdsIntersect()` code which are used in execution flow to check orders and matching validity:
```solidity
/**
 * @notice Checks whether take orders with a higher order intent can be executed
 * @dev This function is called by the main exchange to check whether take orders with a higher order intent can be executed.
        It checks whether orders have the right constraints - i.e they have the right number of items, whether time is still valid
        and whether the nfts intersect
 * @param makerOrder the maker order
 * @param takerItems the taker items specified by the taker
 * @return returns whether order can be executed
 */
function canExecTakeOrder(OrderTypes.MakerOrder calldata makerOrder, OrderTypes.OrderItem[] calldata takerItems)
    external
    view
    override
    returns (bool)
{
    return (makerOrder.constraints[3] <= block.timestamp &&
        makerOrder.constraints[4] >= block.timestamp &&
        areTakerNumItemsValid(makerOrder, takerItems) &&
        doItemsIntersect(makerOrder.nfts, takerItems));
}

/// @dev sanity check to make sure that a taker is specifying the right number of items
function areTakerNumItemsValid(OrderTypes.MakerOrder calldata makerOrder, OrderTypes.OrderItem[] calldata takerItems)
    public
    pure
    returns (bool)
{
    uint256 numTakerItems = 0;
    uint256 nftsLength = takerItems.length;
    for (uint256 i = 0; i < nftsLength; ) {
        unchecked {
            numTakerItems += takerItems[i].tokens.length;
            ++i;
        }
    }
    return makerOrder.constraints[0] == numTakerItems;
}

/**
 * @notice Checks whether tokenIds intersect
 * @dev This function checks whether there are intersecting tokenIds between two order items
 * @param item1 first item
 * @param item2 second item
 * @return returns whether tokenIds intersect
 */
function doTokenIdsIntersect(OrderTypes.OrderItem calldata item1, OrderTypes.OrderItem calldata item2)
    public
    pure
    returns (bool)
{
    uint256 item1TokensLength = item1.tokens.length;
    uint256 item2TokensLength = item2.tokens.length;
    // case where maker/taker didn't specify any tokenIds for this collection
    if (item1TokensLength == 0 || item2TokensLength == 0) {
        return true;
    }
    uint256 numTokenIdsPerCollMatched = 0;
    for (uint256 k = 0; k < item2TokensLength; ) {
        for (uint256 l = 0; l < item1TokensLength; ) {
            if (
                item1.tokens[l].tokenId == item2.tokens[k].tokenId && item1.tokens[l].numTokens == item2.tokens[k].numTokens
            ) {
                // increment numTokenIdsPerCollMatched
                unchecked {
                    ++numTokenIdsPerCollMatched;
                }
                // short circuit
                break;
            }
            unchecked {
                ++l;
            }
        }
        unchecked {
            ++k;
        }
    }

    return numTokenIdsPerCollMatched == item2TokensLength;
}
```

As you can see there is no logic to check that `token IDs` in one collection of order are different and code only checks that total number of tokens in one `order` matches the number of tokens specified and the ids in one order exists in other list defined. function `doTokenIdsIntersect()` checks to see that `tokens ids` in one collection can match list of specified tokens. because of this check lacking there are some scenarios that can cause fund lose for `ERC1155` tokens (normal `ERC721` requires more strange conditions). here is first example:

1. For simplicity, let’s assume collection and timestamp are valid and match for orders and token is `ERC1155`
2. `user1` has signed this order: A:`(user1 BUY 3 NFT IDs[(1,1),(2,1),(3,1)] at 15 ETH)` (buy `1` token of each `id=1,2,3`)
3. `NFT ID[1]` fair price is `1 ETH`, `NFT ID[2]` fair price is `2 ETH`, `NFT ID[3]` fair price is `12 ETH`
4. `attacker` who has 3 of `NFT ID[1]` create this list: B:`(NFT IDs[(1,1), (1,1), (1,1)] )` (list to trade `1`token of `id=1` for 3 times)
5. Attacker call `takeOrders()` with this parameters: makerOrder: A , takerNfts: B
6. Contract logic would check all the conditions and validate and verify orders and their matching (they intersect and total number of token to sell is equal to total number of tokens to buy and all of the B list is inside A list) and perform the transaction.
7. `attacker` would receive `15 ETH` for his 3 token of `NFT ID[1]` and steal `user1` funds. `user1` would receive 3 of `NFT ID[1]` and pays `15 ETH` and even so his order A has been executed he doesn’t receive `NFT IDs[(2,1),(3,1)]` and contract would violates his signed parameters.

This examples shows that in verifying one to many order code should verify that one order’s one collection’s token ids are not duplicates. (the function `doTokenIdsIntersect()` doesn’t check for this).

This scenario is performable to `matchOneToManyOrders()` and `matchOrders()` and but exists in their code (related check logics) too. more important things about this scenario is that it doesn’t require off-chain maching engine to make mistake or malicious act, anyone can call `takeOrders()` if NFT tokens are `ERC1155`. for other `NFT` tokens to perform this attack it requires that `seller==buyer` or some other strange cases (like auto selling when receiving in one contract).

## Recommendation
Add checks to ensure `order`’s one `collection`’s token ids are not duplicate in `doTokenIdsIntersect()`

Agree with assessment. Fixed. <https://github.com/infinitydotxyz/exchange-contracts-v2/commit/c3c0684ac02e0cf1c03cdbee7e68c5a37fa334a8> and removed support for ERC1155

This is an interesting scenario where the same NFT appears multiple times in a match and results in one order being under filled, leading to potential losses for the user. And the attack does not depend on the matching engine. Agree this is High risk.
