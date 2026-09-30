# [M] Upgrading modules via `executeAction`

## Summary
Severity: Medium
Contest weight: 0.5417
Dataset id: 20661
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The issue is an upgrade‑lockout bug that occurs when the protocol upgrades a storage module through Kernel.executeAction while there are still active rental agreements. The upgrade routine reconfigures policies and initializes the new module but does not migrate any on‑chain state or provide a mechanism to stop or withdraw assets that are held by the old module. As a result, assets that were escrowed for rentals created before the upgrade remain locked in the previous contract instance, and the rental cannot be terminated because the stopRent function is no longer reachable. Users therefore experience a situation where they expect to receive their escrowed funds after a rental expires, but the balance shown by the UI stays unchanged or appears as zero for the new module, while the old contract still holds the tokens. The vulnerability was discovered during an audit by writing a proof‑of‑concept test that upgrades the PaymentEscrow module, fast‑forwards time past the rental expiration, and then attempts to stop the rental, which reverts, confirming that the funds are inaccessible. The root cause is the lack of a migration path or a pre‑upgrade safety check that ensures all rentals are either stopped or have a bounded maximum duration before the upgrade is allowed. This condition can be hard to notice because the upgrade transaction itself succeeds without error, giving the impression that the system is functional, while the hidden state in the old contract is silently unreachable. The impact is that renters and lenders who had active rentals at the time of the upgrade lose access to their escrowed tokens, effectively a denial‑of‑service and potential loss of funds. The bug belongs to the class of upgrade‑related state incompatibility bugs, where a proxy or modular contract is replaced without reconciling existing data. To remediate, the protocol should either enforce that no rentals are active before allowing an upgrade (for example by introducing a maximum rental duration and pausing new rentals), or implement a migration interface such as a migrate() function that lets users transfer their rental state and escrowed assets to the new module, or provide an emergency withdrawal path in the old module so that locked funds can be reclaimed.

## Proof of Concept
The protocol has a functionality to [upgrade modules via `Kernel::executeAction()`](https://github.com/re-nft/smart-contracts/blob/main/src/Kernel.sol#L285).

That upgrade functionality [performs some checks, initializes the new modules, and reconfigures policies](https://github.com/re-nft/smart-contracts/blob/main/src/Kernel.sol#L383-L411), but it doesn’t migrate any data, nor transfer any assets.

Modules can hold assets, such as in the case of the `PaymentEscrow`, as well as keeping rentals states in storage.

The [current implementation of the `PaymentEscrow`](https://github.com/re-nft/smart-contracts/blob/main/src/modules/PaymentEscrow.sol) for example doesn’t have any mechanism for migrations, or to stop rentals, or withdraw assets if the module was upgraded via `executeAction()`.

This will result in all previous rentals assets being locked, as rentals can no longer be stopped.

The following POC proves that old rentals can’t be stopped, as well as showing how the old contract is still holding the users funds.

Create a new test in `smart-contracts/test/integration/Upgrade.t.sol` with this code:

```solidity
// SPDX-License-Identifier: BUSL-1.1
pragma solidity ^0.8.20;

import {
    Order,
    FulfillmentComponent,
    Fulfillment,
    ItemType as SeaportItemType
} from "@seaport-types/lib/ConsiderationStructs.sol";

import {Errors} from "@src/libraries/Errors.sol";
import {OrderType, OrderMetadata, RentalOrder} from "@src/libraries/RentalStructs.sol";

import {BaseTest} from "@test/BaseTest.sol";
import {ProtocolAccount} from "@test/utils/Types.sol";

import {SafeUtils} from "@test/utils/GnosisSafeUtils.sol";
import {Safe} from "@safe-contracts/Safe.sol";

import {SafeL2} from "@safe-contracts/SafeL2.sol";
import {PaymentEscrow} from "@src/modules/PaymentEscrow.sol";
import {Proxy} from "@src/proxy/Proxy.sol";

import {Kernel, Actions} from "@src/Kernel.sol";

contract UpgradeDrain is BaseTest {
    function test_StopRent_UpgradedModule() public {
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

        // finalize the base order fulfillment
        RentalOrder memory preUpgradeRental = finalizeBaseOrderFulfillment();

        bytes memory paymentEscrowProxyInitCode = abi.encodePacked(
            type(Proxy).creationCode,
            abi.encode(
                address(paymentEscrowImplementation),
                abi.encodeWithSelector(
                    PaymentEscrow.MODULE_PROXY_INSTANTIATION.selector,
                    address(kernel)
                )
            )
        );

        // <<Upgrade the Escrow contract >>

        PaymentEscrow OLD_ESCRW = ESCRW;

        bytes12 protocolVersion = 0x000000000000000000000420;
        bytes32 salt = create2Deployer.generateSaltWithSender(deployer.addr, protocolVersion);

        vm.prank(deployer.addr);
        PaymentEscrow NEW_ESCRW = PaymentEscrow(create2Deployer.deploy(salt, paymentEscrowProxyInitCode));

        vm.prank(deployer.addr);
        kernel.executeAction(Actions.UpgradeModule, address(NEW_ESCRW));

        // speed up in time past the rental expiration
        vm.warp(block.timestamp + 750);

        bytes32 payRentalOrderHash = create.getRentalOrderHash(preUpgradeRental);

        // assert that the rent still exists
        assertEq(STORE.orders(payRentalOrderHash), true);
        assertEq(STORE.isRentedOut(address(bob.safe), address(erc721s[0]), 0), true);

        // assert that the ERC20 tokens are on the OLD contract
        assertEq(erc20s[0].balanceOf(address(OLD_ESCRW)), uint256(100));
        assertEq(erc20s[0].balanceOf(address(NEW_ESCRW)), uint256(0));

        // assert that the token balances are in the OLD contract and haven't been migrated
        assertEq(OLD_ESCRW.balanceOf(address(erc20s[0])), uint256(100));
        assertEq(NEW_ESCRW.balanceOf(address(erc20s[0])), uint256(0));

        // The rental can no longer be stopped
        vm.expectRevert();
        vm.prank(alice.addr);
        stop.stopRent(preUpgradeRental);
    }
}
```

## Recommendation
Provide a method for users to migrate old rentals to the upgraded contracts, such as a `migrate()` function, executable by them or the protocol.

Another way is to provide a way to stop all rentals before the upgrade, in order to start with a fresh new module, or allow users to stop rentals from old modules.

This is intended behavior. Upgrading modules is seen as an extremely rare thing, which will only be done in the absense of active rentals.

Would probably be more appropriate for this to be QA.

@Alec1017 - How would this state be achieved? If the protocol is seeing broad adoption it seems likely that there are essentially always going to be outstanding rentals with no clear ability to recall them all.

Our co-signing technique allows us to stop signing off on allowing new rentals, so if we wanted to upgrade everything, we would stop co-signing on orders that use the old contracts and wait for all active orders to expire.

Of course, this only works when a max rent duration is introduced, which is a planned mitigation for this audit.

Thanks. I think M is the correct severity since the code as audited doesn’t practically allow for this functionality to work without major implications. Even with a max duration, essentially pausing the protocol for that long is a DOS and probably means M is correct.

Hey there, I dont think I was very clear about the point of upgrading in this manner. Upgrading via the kernel is not meant to be the “normal” way a storage contract is upgraded, this is why they’re proxies as well.

Our protocol is modular, which allows the deployment of multiple versions of the same contracts. In the future, you could imagine multiple iterations of our protocol being introduced, which can be rolled in and out simultaneously. We can choose to deprecate one storage module by only allowing people to stop rentals via the situation i described above, and also allow them to initiate rentals with newer versions.

Hopefully this is helpful context!
