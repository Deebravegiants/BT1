# [M] `RentPayload`’s signature can be replayed

## Summary
Severity: Medium
Contest weight: 0.7212
Dataset id: 20667
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a replayability flaw in the rental protocol where the signature attached to a RentPayload can be reused to satisfy multiple PAY orders that share the same zonehash. The root cause is that the RentPayload structure does not contain any field that uniquely identifies a single order, such as a nonce or the order hash, and the contract’s validation logic only checks that the signature is authentic and not expired. Because there is no replay protection, an attacker who obtains a valid, unexpired payload and its signature can submit the same payload to any number of PAY orders that have identical metadata, causing the contract to accept each submission as a distinct fulfillment. Exploitation proceeds by first creating or observing a PAY order with a given metadata set, then extracting the payload and signature from the order’s extraData. The attacker then calls the fulfillment function repeatedly, passing the same payload and signature for each target order. Since the signature verification succeeds each time and the expiration check still passes, the contract records each fulfillment and transfers the rental earnings to the attacker. The impact is that lenders lose the expected rental payments, the escrow balance is drained, and the protocol’s accounting assumptions are broken – funds that should be allocated to distinct lenders are instead captured by a single malicious renter. This condition occurs whenever multiple PAY orders are created with identical OrderMetadata, which is likely because the metadata fields (order type, duration, hooks, extra data) are simple and often repeated. All participants – lenders, renters, and the protocol itself – are affected because the financial outcome is altered without any visible error; from a user’s point of view the UI may show rentals being fulfilled as normal, but the expected balances for lenders remain unchanged or become zero, and the attacker sees unexpected earnings. The issue was discovered during a formal audit when a test case demonstrated that extraData fields were identical across orders from different lenders and that stopping the rentals removed the orders from storage while still allowing the same payload to be reused. The flaw is hard to notice because the signature verification passes and there is no explicit replay check, so normal transaction logs do not reveal abnormal behavior. To remediate, the RentPayload should include a unique identifier such as the orderHash (or a nonce) and the contract must verify that each payload has not been used before processing a fulfillment. This change ensures that each rental order can only be satisfied once, restoring the intended one‑to‑one relationship between a payload signature and a specific rental agreement and preventing unauthorized multiple earnings.

## Proof of Concept
The rental process in `reNFT` can simply be described as follows:

1. `lender` create either `BASE` or `PAY` order, which includes a `zoneHash`.
2. `renter` fulfills the rental order by providing certain items, including `fulfiller`, `payload`(a structured data of `RentPayload`), and its corresponding signature.
3. Once the rental order is created, `Create#validateOrder()` will be executed to verify if the rental order is valid:

   * decode `payload` and its `signature` from `zoneParams.extraData`
   * Check if the signature is expired by comparing `payload.expiration` and `block.timestamp`
   * Recover the signer from `payload` and its `signature` and check if the signer is protocol signer
   * check if `zonehash` is equal to the derived hash of `payload.metadata`

Let’s take a look at `RentPayload` and its referenced structures:

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

By observing all items in `Rentpayload`, it’s obvious that there is no way to verify whether the signature of a `payload` has been used or not. The signature verification can always be passed as long as it has not expired.

If multiple `PAY` rental orders own the same `metadata`, a user could potentially utilize their `payload` and unexpired `signature` to fulfill all these rental orders and acquire rental earnings. Since `OrderMetadata` structure is very simple, the chance that two different orders own same `metadata` could be high.

Update testcase `test_stopRentBatch_payOrders_allDifferentLenders()`in [`StopRentBatch.t.sol`](https://github.com/re-nft/smart-contracts/blob/3ddd32455a849c3c6dc3c3aad7a33a6c9b44c291/test/integration/StopRentBatch.t.sol) with below codes and run `forge test --match-test test_stopRentBatch_payOrders_allDifferentLenders`:

```solidity
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
        console.logBytes(ordersToFulfill[i*2].advancedOrder.extraData);

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

## Recommendation
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

The PR [here](https://github.com/re-nft/smart-contracts/pull/10) - Prevents `RentPayload` replayability and ensures that orders must be unique by disallowing partial orders from seaport.
