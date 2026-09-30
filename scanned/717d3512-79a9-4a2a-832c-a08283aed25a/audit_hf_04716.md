# [M] Not all ERC20 tokens can be bridged because of hardcoded predicate

## Summary
Severity: Medium
Contest weight: 0.6849
Dataset id: 22519
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
PREDICATE_ADDRESS in BridgeRelay.sol is hardcoded to the ERC20Predicate. This means that any tokens that use other predicates will not be bridgeable.

When the BridgeRelay.transferERCToBridge gets called, it approves the hardcoded ERC20Predicate to use the ERC20 tokens. However, the bridge uses more than one predicate to lock the tokens. Here the bridge retrieves the predicate address based on the type of token to be bridged. If a token that uses different predicate than the hardcoded is sent to the BridgeRelay, it will be forever stuck there since the right predicate will not have approval to transfer it. There also exists a risk that a token can change its predicate at any time.

Tokens that use different predicate will be forever stuck in the contract.
```solidity
function transferERCToBridge(IERC20 token) internal {
    //zero out approvals
    token.forceApprove(PREDICATE_ADDRESS, 0);
    // increase approval to necessary amount
    token.safeIncreaseAllowance(
        PREDICATE_ADDRESS,
        token.balanceOf(address(this))
    );
    //deposit
    POS_BRIDGE.depositFor(
        address(this),
        address(token),
        abi.encodePacked(token.balanceOf(address(this)))
    );
}
```
```solidity
address predicateAddress = typeToPredicate[tokenType];
require(
    predicateAddress != address(0),
    "RootChainManager: INVALID_TOKEN_TYPE"
);
require(
    user != address(0),
    "RootChainManager: INVALID_USER"
);
ITokenPredicate(predicateAddress).lockTokens(
    _msgSender(),
    user,
    rootToken,
    depositData
);
```

## Recommendation
Instead of hardcoding the predicate, query the bridge when transferring the ERC20 token.
```solidity
function transferERCToBridge(IERC20 token) internal {
    bytes32 tokenType = POS_BRIDGE.tokenToType(address(token));
    bytes32 predicateAddress = POS_BRIDGE.typeToPredicate(tokenType);
    //zero out approvals
    token.forceApprove(PREDICATE_ADDRESS, 0);
    // increase approval to necessary amount
    token.safeIncreaseAllowance(
        predicateAddress,
        token.balanceOf(address(this))
    );
    //deposit
    POS_BRIDGE.depositFor(
        address(this),
        address(token),
        abi.encodePacked(token.balanceOf(address(this)))
    );
}
```
