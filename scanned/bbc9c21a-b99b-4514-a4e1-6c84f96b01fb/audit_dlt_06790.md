# [M] `RentPayload`'s signature can be replayed

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-01-renft
Published: 2024-01-16
Source: https://github.com/code-423n4/2024-01-renft-findings/issues/162
Type: code-finding

## Details
# Lines of code

https://github.com/re-nft/smart-contracts/blob/3ddd32455a849c3c6dc3c3aad7a33a6c9b44c291/src/policies/Create.sol#L760-L763


# Vulnerability details

## Impact
A malicious user could potentially fulfill all `PAY` orders that own the same value of `zonehash`

## Proof of Concept
The rental process in `reNFT` can simply be described as follows:
1. `lender` create either `BASE` or `PAY` order, which includes a `zoneHash`.
2. `renter` fulfills the rental order by providing certain items, including `fulfiller`, `payload`(a structured data of `RentPayload`), and its corresponding signature.
3. Once the rental order is created, `Create#validateOrder()` will be executed to verify if the rental order is valid:
   - decode `payload` and its `signature` from `zoneParams.extraData`
   - Check if the signature is expired by comparing `payload.expiration` and `block.timestamp`
   - Recover the signer from `payload` and its `signature` and check if the signer is protocol signer
   - check if `zonehash` is equal to the derived hash of `payload.metadata`

Let's take a look at `RentPayload` and its referenced structures:
```solidity
struct RentPayload {
    OrderFulfillment fulfillment;
    OrderMetadata metadata;
    uint256 expiration;
    address intendedFulfiller;
}
struct OrderFulfillment {
    // Rental wallet address.
    address recipient;
}
struct OrderMetadata {
    // Type of order being created.
    OrderType orderType;
    // Duration of the rental in seconds.
    uint256 rentDuration;
    // Hooks that will act as middleware for the items in the order.
    Hook[] hooks;
    // Any extra data to be emitted upon order fulfillment.
    bytes emittedExtraData;
}
```
By observing all items in `Rentpayload`, it's obvious that there is no way to verify whether the signature of a `payload` has been used or not. The signature verification can always be passed as long as it has not expired.

If multiple `PAY` rental orders own the same `metadata`, a user could potentially utilize their `payload` and unexpired `signature` to fulfill all these rental orders and acquire rental earnings. Since `OrderMetadata` structure is very simple, the chance that two different orders own same `metadata` could be high.

Update testcase `test_stopRentBatch_payOrders_allDifferentLenders()`in [`StopRentBatch.t.sol`](https://github.com/re-nft/smart-contracts/blob/3ddd32455a849c3c6dc3c3aad7a33a6c9b44c291/test/integration/StopRentBatch.t.sol) with below codes and run `forge test --match-test test_stopRentBatch_payOrders_allDifferentLenders`:
```diff
    function test_stopRentBatch_payOrders_allDifferentLenders() public {
        // create an array of offerers
        ProtocolAccount[] memory offerers = new ProtocolAccount[](3);
        offerers[0] = alice;
        offerers[1] = bob;
        offerers[2] = carol;

        // for each offerer, create an order and a fulfillment
        for (uint256 i = 0; i < offerers.length; i++) {
            // create a PAY order
            createOrder({
                offerer: offerers[i],
                orderType: OrderType.PAY,
                erc721Offers: 1,
                erc1155Offers: 0,
                erc20Offers: 1,
                erc721Considerations: 0,
                erc1155Considerations: 0,
                erc20Considerations: 0
            });

            // finalize the pay order creation
            (
                Order memory payOrder,
                bytes32 payOrderHash,
                OrderMetadata memory payOrderMetadata
            ) = finalizeOrder();

            // create a PAYEE order. The fulfiller will be the offerer.
            createOrder({
                offerer: dan,
                orderType: OrderType.PAYEE,
                erc721Offers: 0,
                erc1155Offers: 0,
                erc20Offers: 0,
                erc721Considerations: 1,
                erc1155Considerations: 0,
                erc20Considerations: 1
            });

            // finalize the pay order creation
            (
                Order memory payeeOrder,
                bytes32 payeeOrderHash,
                OrderMetadata memory payeeOrderMetadata
            ) = finalizeOrder();

            // create an order fulfillment for the pay order
            createOrderFulfillment({
                _fulfiller: dan,
                order: payOrder,
                orderHash: payOrderHash,
                metadata: payOrderMetadata
            });

            // create an order fulfillment for the payee order
            createOrderFulfillment({
                _fulfiller: dan,
                order: payeeOrder,
                orderHash: payeeOrderHash,
                metadata: payeeOrderMetadata
            });
+           console.logBytes(ordersToFulfill[i*2].advancedOrder.extraData);

            // add an amendment to include the seaport fulfillment structs
            withLinkedPayAndPayeeOrders({
                payOrderIndex: (i * 2),
                payeeOrderIndex: (i * 2) + 1
            });
        }

        // finalize the order pay/payee order fulfillments
        RentalOrder[] memory rentalOrders = finalizePayOrdersFulfillment();

        // pull out just the PAY orders
        RentalOrder[] memory payRentalOrders = new RentalOrder[](3);
        for (uint256 i = 0; i < rentalOrders.length; i++) {
            if (rentalOrders[i].orderType == OrderType.PAY) {
                payRentalOrders[i / 2] = rentalOrders[i];
            }
        }

        // speed up in time past the rental expiration
        vm.warp(block.timestamp + 750);

        // renter stops the rental order
        vm.prank(dan.addr);
        stop.stopRentBatch(payRentalOrders);

        // for each rental order stopped, perform some assertions
        for (uint256 i = 0; i < payRentalOrders.length; i++) {
            // assert that the rental order doesnt exist in storage
            assertEq(STORE.orders(payRentalOrders[i].seaportOrderHash), false);

            // assert that the token is no longer rented out in storage
            assertEq(
                STORE.isRentedOut(
                    payRentalOrders[i].rentalWallet,
                    address(erc721s[0]),
                    i
                ),
                false
            );

            // assert that the ERC721 is back to its original owner
            assertEq(erc721s[0].ownerOf(i), address(offerers[i].addr));

            // assert that each offerer made a payment
            assertEq(erc20s[0].balanceOf(offerers[i].addr), uint256(9900));
        }

        // assert that the payments were pulled from the escrow contract
        assertEq(erc20s[0].balanceOf(address(ESCRW)), uint256(0));

        // assert that the fulfiller was paid for each order
        assertEq(erc20s[0].balanceOf(dan.addr), uint256(10300));
    }
```
You may find out that all `extraData` are same although the rental orders are created by different lenders.
## Tools Used
Manual review
## Recommended Mitigation Steps
Introduces a field into `RentPayload` to ensure every `payload` unique. It is feasible using `orderHash` of the rental order:
```solidity
struct RentPayload {
    bytes32 orderHash;
    OrderFulfillment fulfillment;
    OrderMetadata metadata;
    uint256 expiration;
    address intendedFulfiller;
}
```


## Assessed type

Other
