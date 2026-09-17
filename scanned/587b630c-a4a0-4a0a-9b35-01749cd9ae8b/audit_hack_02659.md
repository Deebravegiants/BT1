# [M] Queue contract address and Auction contract address from VaultAdmin.sol can be updated even when there are open deposit requests in the queue or open unsettled auctions live

## Summary
Severity: Medium
Reporter: ctf_sec
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultAdmin.sol#L28
Type: audit-issue

## Details
# Queue contract address and Auction contract address from VaultAdmin.sol can be updated even when there are open deposit requests in the queue or open unsettled auctions live

## Summary

Queue contract address and Auction contract address from VaultAdmin.sol can be updated even when there are open deposit requests in the queue or open unsettled auctions live 

## Vulnerability Detail

the admin can set queue contract address and auction contract address from VaultAdmin.sol

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultAdmin.sol#L28

```solidity
   function setAuction(address newAuction) external onlyOwner {
        VaultStorage.Layout storage l = VaultStorage.layout();
        require(newAuction != address(0), "address not provided");
        require(newAuction != address(l.Auction), "new address equals old");

        emit AuctionSet(l.epoch, address(l.Auction), newAuction, msg.sender);

        l.Auction = IAuction(newAuction);
    }
```

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultAdmin.sol#L142

and 

```solidity
     function setQueue(address newQueue) external onlyOwner {
        VaultStorage.Layout storage l = VaultStorage.layout();
        require(newQueue != address(0), "address not provided");
        require(newQueue != address(l.Queue), "new address equals old");

        emit QueueSet(l.epoch, address(l.Queue), newQueue, msg.sender);

        l.Queue = IQueue(newQueue);
    }
```

The Queue acts as a liquidity buffer for the Vault, LP’s must deposit their collateral into the Queue prior to its deposit into the Vault at the end of the epoch.

The Queue contract relies on the vault contract to call

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/Queue.sol#L202

```solidity
function processDeposits() external onlyVault
```

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/Queue.sol#L219

to set l.pricePerShare[currentTokenId]

```solidity
        if (shares <= 0) {
            pricePerShare = 0;
        } else if (claimTokenSupply > 0) {
            pricePerShare = (pricePerShare * shares) / claimTokenSupply;
        }
```

this parameter is used later when user want to redeem the token into the share in the function previewUndeemedShare()

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/QueueInternal.sol#L124

```solidity
        uint256 unredeemedShares = _previewUnredeemed(tokenId, owner);
```

inside _previewUnredeemed(tokenId, owner) function

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/QueueInternal.sol#L169

```solidity
    function _previewUnredeemed(uint256 tokenId, address account)
        internal
        view
        returns (uint256)
    {
        QueueStorage.Layout storage l = QueueStorage.layout();
        uint256 balance = _balanceOf(account, tokenId);
        return (balance * l.pricePerShare[tokenId]) / ONE_SHARE;
    }
```


Queue contract address and Auction contract address from VaultAdmin.sol can be updated even when there are open deposit request in the queue

Then the no one can call processDeposits() for the old queue address. 

The user would not able to redeem the share using their token from the Queue and the deposit request will not be processed.

------

The Auction contract sells options once per week using a Dutch Auction format

the auction contract relies on the vault contract to call

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/Auction.sol#L354

```solidity
 function transferPremium(uint64 epoch)
```

and 

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/Auction.sol#L381

```solidity
function processAuction(uint64 epoch) external onlyVault
```

to complete the auction cycle.

Auction contract address from VaultAdmin.sol can be updated even when the auction is not settled.

Then no one can call transferPremium() and processAuction() for the old auction contract address

The premium balance would be locked.

the user token would be locked because the auction status is never AuctionStorage.Status.PROCESSED,
then user cannot call withdraw function.

because in the processAuction() function, the auction status is updated to PROCESSED

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/Auction.sol#L407

```solidity
        auction.processedTime = block.timestamp;
        auction.status = AuctionStorage.Status.PROCESSED;
        emit AuctionStatusSet(epoch, auction.status);
```

then user can withdraw the fund via 

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/Auction.sol#L283

```solidity
    function withdraw(uint64 epoch) external nonReentrant {
        AuctionStorage.Layout storage l = AuctionStorage.layout();
        AuctionStorage.Auction storage auction = l.auctions[epoch];

        require(
            AuctionStorage.Status.PROCESSED == auction.status ||
                AuctionStorage.Status.CANCELLED == auction.status,
            "status != processed || cancelled"
        );
```

if the auction status is never PROCESSED after the auction is finalized, the user can never call withdraw function.

## Impact

User token can be locked in Auction.sol if the auction becomes orphan when the admin update the auction contract address without settling the old auction.

User cannot redeem their shares using token if the queue becomes orphan when the admin update the queue address without calling
processDeposit to process the deposit.

## Code Snippet

## Tool used

Manual Review

## Recommendation

We recommend the project check if the deposit is processed in the Queue and if the auction is settled in the Auction contract
before the queue contract address and auction contract address can be updated by admin.

The implementation is shown below

in Queue.contract, add

```solidity
  function isPendingDeposit() returns (bool) {
  	// contain logic to check if all deposit requests are processed
  }
```

in Auction.sol Contract

```solidity
  function isPendingAuction() returns (bool) {
  	// contain logic check if the auction is settled.
  }
```

and in VaultAdmin.sol,

we add the check below inside function setQueue

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultAdmin.sol#L142

```solidity
 VaultStorage.Layout storage l = VaultStorage.layout();
 require(!IQueue(l).isPendingDeposit, "Has pending deposit");
```

and the check below inside the function setAuction.sol

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultAdmin.sol#L28

```solidity
 VaultStorage.Layout storage l = VaultStorage.layout();
 require(!IAuction(l).isPendingAuction, "Auction is not settled");
```
