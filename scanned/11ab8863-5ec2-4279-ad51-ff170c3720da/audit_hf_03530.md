# [M] `onlyCentrifugeChainOrigin`

## Summary
Severity: Medium
Contest weight: 0.2141
Dataset id: 19292
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In `AxelarRouter.sol`, we need to ensure the legitimacy of the `execute()` method execution, mainly through two methods:

1. `axelarGateway.validateContractCall()` to validate if the `command` is approved or not.
2. `onlyCentrifugeChainOrigin()` is used to validate that `sourceChain` `sourceAddress` is legal.

Let’s look at the implementation of `onlyCentrifugeChainOrigin()`:

    modifier onlyCentrifugeChainOrigin(string calldata sourceChain, string calldata sourceAddress) {        
        require(msg.sender == address(axelarGateway), "AxelarRouter/invalid-origin");
        require(
            keccak256(bytes(axelarCentrifugeChainId)) == keccak256(bytes(sourceChain)),
            "AxelarRouter/invalid-source-chain"
        );
        require(
            keccak256(bytes(axelarCentrifugeChainAddress)) == keccak256(bytes(sourceAddress)),
            "AxelarRouter/invalid-source-address"
        );
        _;
    }

The problem is that this restriction `msg.sender == address(axelarGateway)`.

When we look at the official `axelarGateway.sol` contract, it doesn’t provide any call external contract’s`execute()` method.

So `msg.sender` cannot be `axelarGateway`, and the official example does not restrict `msg.sender`.

The security of the command can be guaranteed by `axelarGateway.validateContractCall()`, `sourceChain`, `sourceAddress`.

There is no need to restrict `msg.sender`.

`axelarGateway` code address

Can’t find anything that calls `router.execute()`.

## Recommendation
Remove `msg.sender` restriction

    modifier onlyCentrifugeChainOrigin(string calldata sourceChain, string calldata sourceAddress) {        
        require(
            keccak256(bytes(axelarCentrifugeChainId)) == keccak256(bytes(sourceChain)),
            "AxelarRouter/invalid-source-chain"
        );
        require(
            keccak256(bytes(axelarCentrifugeChainAddress)) == keccak256(bytes(sourceAddress)),
            "AxelarRouter/invalid-source-address"
        );
        _;
    }
