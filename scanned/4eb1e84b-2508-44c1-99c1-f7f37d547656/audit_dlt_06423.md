# [M] Inconsistency in Handling WETH in `eth::most::receiveRequest`

## Summary
Severity: Medium
Chain: Smart contract
Component: Most--Aleph-Zero-Bridge
Published: 2024-03-21
Source: https://github.com/hats-finance/Most--Aleph-Zero-Bridge-0xab7c1d45ae21e7133574746b2985c58e0ae2e61d/issues/34
Type: hats-finding

## Details
**Github username:** @0xmahdirostami
**Twitter username:** 0xmahdirostami
**Submission hash (on-chain):** 0x82d2682c8143b7687373b20de9007b5e79b82735a356e972857eb3f4a6381a11
**Severity:** medium

**Description:**
**Description**\
In the `eth::most::receiveRequest` function, there's a check `if (_destTokenAddress == wethAddress)`. The issue here is that using `wethAddress` to differentiate between tokens and ETH will cause issues.

**Scenario**

Consider a contract, Contract B, that only works with WETH and doesn't accept ETH. Here's what might happen:

1. Contract B sends some WETH to the bridge contract.
2. Later on, Contract B wants to retrieve the WETH.
3. However, since in `receiveRequest` WETH tokens are converted to ETH, the transfer fails

**Impact**  
Users might expect to receive WETH but will actually receive ETH instead. This could lead to unexpected behavior, especially for contracts that only accept tokens and not ETH. This would result in a loss of funds for users, although recoverable by the owner.


**POC**
- cd eth
- npm install --save-dev @nomicfoundation/hardhat-foundry
- npm install --save-dev @nomicfoundation/hardhat-toolbox
- import this in your Hardhat config: require ("@nomicfoundation/hardhat-foundry");
- npx hardhat init-foundry
- forge test --fork-url "RPC Link" --fork-block-number "19481680" --match-path test/poc.t.sol -vvvvv

```solidity
// SPDX-License-Identifier: MIT

pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import "../contracts/Most.sol";
import "forge-std/console2.sol";
import "../contracts/Token.sol";

// contract that work just with WETH, accept WETH frrom most::eth
contract NoETHContract {
    fallback() external {
        revert("This contract does not accept Ether.");
    }
}

contract POC is Test {
    event EthTransferFailed(bytes32 requestHash);

    Most public most;
    NoETHContract public noETH;

    address alice = 0x2fEb1512183545f48f6b9C5b4EbfCaF49CfCa6F3; //weth whale
    address public WETH = 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2;
    address public WBTC = 0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599;

    function setUp() public {
        most = new Most();
        noETH = new NoETHContract();
    }

    function test_poc() public {
        // setup
        address[] memory addresses = new address[](1);
        addresses[0] = alice;
        most.initialize(addresses, 1, alice, payable(WETH));
        vm.startPrank(alice);
        most.addPair(bytes32(uint256(uint160(WETH))), bytes32(uint256(uint160(WBTC))));
        most.unpause();

        // send request (send weth)
        bytes32 destTokenAddress = bytes32(uint256(uint160(WETH)));
        uint256 amount = 1 ether;
        bytes32 receiver = bytes32(uint256(uint160(address(noETH))));
        Token(WETH).approve(address(most), amount);
        most.sendRequest(destTokenAddress, amount, receiver);

        // now wants weth back and request weth, but contract just send ETH
        uint256 _committeeId = 0;
        bytes32 destReceiverAddress = bytes32(uint256(uint160(address(noETH))));
        uint256 _requestNonce = 0;
        bytes32 requestHash =
            keccak256(abi.encodePacked(_committeeId, destTokenAddress, amount, destReceiverAddress, _requestNonce));
        vm.expectEmit(address(most));
        emit EthTransferFailed(requestHash);
        most.receiveRequest(requestHash, _committeeId, destTokenAddress, amount, destReceiverAddress, _requestNonce);
    }
}
```


**Revised Code File (Optional)**  
Consider using a custom address to differentiate between ETH and other tokens. This would ensure consistency in handling WETH transactions and prevent the issue described above.

```diff
+    address public eth = address(0x01321231);

     /// @notice Aggregates relayer signatures and returns the locked tokens.
     /// @dev When the ether is being bridged and the receiver is a contract
     /// that does not accept ether or fallback function consumes more than `GAS_LIMIT` gas units,
@@ -205,7 +207,7 @@ contract Most is Initializable, UUPSUpgradeable, Ownable2StepUpgradeable, Pausab
             address _destTokenAddress = bytes32ToAddress(destTokenAddress);
             address _destReceiverAddress = bytes32ToAddress(destReceiverAddress);
             // return the locked tokens
-            if (_destTokenAddress == wethAddress) {
+            if (_destTokenAddress == eth) {
                 (bool unwrapSuccess,) = wethAddress.call(abi.encodeCall(IWETH9.withdraw, (amount)));
                 if (!unwrapSuccess) revert UnwrappingEth();
                 (bool sendNativeEthSuccess,) = _destReceiverAddress.call{value: amount, gas: GAS_LIMIT}("");
```
