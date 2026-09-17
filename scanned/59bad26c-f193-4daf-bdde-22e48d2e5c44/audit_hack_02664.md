# [H] function _redeemMax in Queue.sol has unbounded gas consumption for loop and can block user from depositing fund.

## Summary
Severity: High
Reporter: ctf_sec
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/Queue.sol#L94
Type: audit-issue

## Details
# function _redeemMax in Queue.sol has unbounded gas consumption for loop and can block user from depositing fund.

## Summary

function _redeemMax in Queue.sol has unbounded gas consumption for loop and can block user from depositing fund.

## Vulnerability Detail

when user deposit fund via Queue.sol

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/Queue.sol#L94 

```solidity
 function deposit(uint256 amount)
```

and 

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/Queue.sol#L110

```solidity
     function swapAndDeposit(IExchangeHelper.SwapArgs calldata s)
```

the function _deposit is called,

then inside the function _deposit in QueueInternal.sol, we call redeem first

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/QueueInternal.sol#L90

```solidity
        // prior to making a new deposit, the vault will redeem all available claim tokens
        // in exchange for the pro-rata vault shares
        _redeemMax(msg.sender, msg.sender);
```

but the logic inside redeemMax has unbounded gas consumption for loop. 

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/QueueInternal.sol#L140

```solidity
    /**
     * @notice exchanges all claim tokens for vault shares
     * @param receiver vault share recipient
     * @param owner claim token holder
     */
    function _redeemMax(address receiver, address owner) internal {
        uint256[] memory tokenIds = _tokensByAccount(owner);
        uint256 currentTokenId = QueueStorage._getCurrentTokenId();

        for (uint256 i; i < tokenIds.length; i++) {
            uint256 tokenId = tokenIds[i];
            if (tokenId != currentTokenId) {
                _redeem(tokenId, receiver, owner);
            }
        }
    }
```

the for loop below can consume unbounded gas because inside each for loop _redeem is also called.

```solidity
for (uint256 i; i < tokenIds.length; i++) {
```

It the for loop run out of gas, the transaction fails and the user can be blocked from depositing fund.

and the function below can also fail because gas is running out

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/Queue.sol#L175

```solidity
    /**
     * @inheritdoc IQueue
     */
    function redeemMax() external nonReentrant {
        _redeemMax(msg.sender, msg.sender);
    }

    function redeemMax(address receiver) external nonReentrant {
        _redeemMax(receiver, msg.sender);
    }

    /**
     * @inheritdoc IQueue
     */
    function redeemMax(address receiver, address owner) external nonReentrant {
        require(
            owner == msg.sender || isApprovedForAll(owner, msg.sender),
            "ERC1155: caller is not owner nor approved"
        );

        _redeemMax(receiver, owner);
    }
```

## Impact

The unbounded for loop in _redeemMax can block user from depositing fund.

## Code Snippet

## Tool used

Manual Review, hardhat

## Recommendation

We recommend the project remove the unbounded for loop or make the for loop bounded, for example,

we let the for loop run at most 10 iteration and we know we call redeem function at most 10 times.
