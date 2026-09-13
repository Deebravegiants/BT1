# [H] User can lose their token without getting any shares when calling redeem function in Queue.sol if the pricePerShares for an epoch is 0

## Summary
Severity: High
Reporter: ctf_sec
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/Queue.sol#L145
Type: audit-issue

## Details
# User can lose their token without getting any shares when calling redeem function in Queue.sol if the pricePerShares for an epoch is 0

## Summary

User can lose their token without gettting any shares when calling redeem function in Queue.sol in the pricePerShares is 0

## Vulnerability Detail

when user wants to redeem the token for vault share, the code below is called

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/Queue.sol#L145

```solidity
    function redeem(uint256 tokenId) external nonReentrant {
        _redeem(tokenId, msg.sender, msg.sender);
    }
```

the logic for _redeem is shown below, first the logic calculate how many unredeemShares can be redeemed via
_prevviewUnredeemed, then user token is burned and shares is transferred into the user.

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/QueueInternal.sol#L123

```solidity
        uint256 balance = _balanceOf(owner, tokenId);
        uint256 unredeemedShares = _previewUnredeemed(tokenId, owner);

        // burns claim tokens held by owner
        _burn(owner, tokenId, balance);
        // transfers unredeemed share amount to the receiver
        require(Vault.transfer(receiver, unredeemedShares), "transfer failed");

        uint64 epoch = QueueStorage._getEpoch();
        emit Redeem(epoch, receiver, owner, unredeemedShares);
```

however, if unredeemedShares is 0, user can lose their token without getting any values.

we need to look into the logic inside _previewUnredeemed

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

the shares is affected by 

```solidity
  l.pricePerShare[tokenId]
```

is either balance or l.pricePerShare[tokenId] is 0, then the previewed share amount is 0.

Can l.pricePerShare[tokenId] is 0?

Yes. this value is set inside the function in Queue.sol

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/Queue.sol#L202

```solidity
function processDeposits() external onlyVault
```

when this function is called,

the  l.pricePerShare[tokenId] is set

```solidity
      uint256 shares = Vault.deposit(deposits, address(this));

        // the shares returned by the vault represent a pro-rata share of the vault tokens. these
        // shares are used to calculate a price-per-share based on the supply of claim tokens for
        // that epoch. the price-per-share is used as an exchange rate of claim tokens to vault
        // shares when a user withdraws or redeems.
        uint256 currentTokenId = QueueStorage._getCurrentTokenId();
        uint256 claimTokenSupply = _totalSupply(currentTokenId);
        uint256 pricePerShare = ONE_SHARE;

        if (shares <= 0) {
            pricePerShare = 0;
        } else if (claimTokenSupply > 0) {
            pricePerShare = (pricePerShare * shares) / claimTokenSupply;
        }

        QueueStorage.Layout storage l = QueueStorage.layout();

        // the price-per-share can be queried if the claim token id is provided
        l.pricePerShare[currentTokenId] = pricePerShare;

```

note if the shares returned by vault is 0, then the pricePerShare will be 0 given 

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/Queue.sol#L206

```solidity
uint256 shares = Vault.deposit(deposits, address(this));
```

and (by the way, the share is a uint256 type and should not be smaller than 0)

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/Queue.sol#L217

```solidity
      if (shares <= 0) {
            pricePerShare = 0;
```

## Consider the POC below

1. The vault call 

```solidity
function processDeposits() external onlyVault
```

and shares deposited into the vault is 0,

then pricePerShares is 0 and 

```solidity
   l.pricePerShare[currentTokenId] = pricePerShare = 0;
```

2. when user wants to redeem the token for shares,

```solidity
_previewUnredeemed(uint256 tokenId, address account)
```

returns 0 and unredeemedShares is 0

3. The user's token is burned without any share given

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/QueueInternal.sol#L127

```solidity
        // burns claim tokens held by owner
        _burn(owner, tokenId, balance);
        // transfers unredeemed share amount to the receiver
        require(Vault.transfer(receiver, unredeemedShares), "transfer failed");
```

## Impact

User can lose their token without getting any shares when calling redeem function in Queue.sol in the pricePerShares is 0

## Code Snippet

## Tool used

Manual Review, hardhat

## Recommendation

We recommand adding check to make sure the unredeemed share is not 0 and make sure the price per share is not 0

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/Queue.sol#L206


```solidity
uint256 shares = Vault.deposit(deposits, address(this));
require(shares > 0, invalid share amount);
```

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/QueueInternal.sol#L124

```solidity
uint256 unredeemedShares = _previewUnredeemed(tokenId, owner);
require(unredeemedShares > 0, 'invalid share amount');
```
