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




_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-02-renft-mitigation-findings/issues/28_
