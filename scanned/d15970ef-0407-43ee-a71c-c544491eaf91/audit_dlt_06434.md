# [H] Staking Functionality is broken for approved addresses by owners of  the ERC20 tokens

## Summary
Severity: High
Chain: Smart contract
Component: Convergence---Convex-integration
Published: 2024-05-03
Source: https://github.com/hats-finance/Convergence---Convex-integration-0xb3df23e155b74ad2b93777f58980d6727e8b40bb/issues/50
Type: hats-finding

## Details
**Github username:** @0xumarkhatab
**Twitter username:** 0xumarkhatab
**Submission hash (on-chain):** 0x9e7d3e6658f64e6bac35f885204a474a01ef1278ef7397708688d284b003bbe1
**Severity:** high

**Description:**
**Description**\
Most functions inside the staking contracts requires the receiver or `msg.sender` to be the `strict owner` of the token they are using.
However , this functionality should also be available for `approved addresses ` of those token owners.

**Attack Scenario**\
Let's take a look at the following code snippets

stakingPositionService#deposit

```solidity
 function deposit(uint256 tokenId, uint256 cvgCvxAmount, DepositCvxData calldata cvxData) external {
        _deposit(tokenId, cvgCvxAmount, cvxData, false);
    }
    function _deposit(
        uint256 tokenId,
        uint256 cvgCvxAmount,
        DepositCvxData memory cvxData,
        bool isEthDeposit
    ) internal {
        // snip
        if (tokenId != 0) {
            /// @dev Fetches, for the tokenId, the owner, the StakingPositionService linked to and the timestamp of unlocking
            _cvxStakingPositionManager.checkIncreaseDepositCompliance(tokenId, msg.sender);
            _tokenId = tokenId;
        }
        // snip

        
    }
```

stakingServiceBase

```solidity

  modifier checkCompliance(uint256 tokenId) {
        stakingPositionManager.checkTokenFullCompliance(tokenId, msg.sender);
        _;
    }
    

    function claimCvgRewards(uint256 tokenId) external checkCompliance(tokenId) {
        //snip
    }
        function claimCvgCvxRewards(
        uint256 _tokenId,
        uint256 _minCvgCvxAmountOut,
        bool _isConvert
    ) external checkCompliance(_tokenId) {
        //snip
    }
```

stakingPositionManager contract 
```solidity
    function checkTokenFullCompliance(uint256 tokenId, address receiver) external view {
        /// @dev Verify that receiver is always the NFT owner
        require(receiver == ownerOf(tokenId), "TOKEN_NOT_OWNED");
        /// @dev As the StakingPositionManager is the NFT contract, we verify that this ID has been created from this StakingPositionService
        require(msg.sender == stakingPerTokenId[tokenId], "WRONG_STAKING");
        /// @dev We verify that the tokenId is not timelocked
        require(unlockingTimestampPerToken[tokenId] < block.timestamp, "TOKEN_TIMELOCKED");
    }

  * @dev Verifies the compliance of a position to increase the deposit amount on it.
     *      Checks that the transaction is done from the staking contract linked to the token ID.
     *      Checks that the position is owned by the account.
     * @param tokenId of the staking position
     * @param receiver Receiver address of the Staking Position NFT
     */
    function checkIncreaseDepositCompliance(uint256 tokenId, address receiver) external view {
        /// @dev Verify that receiver is always the NFT owner
        require(receiver == ownerOf(tokenId), "TOKEN_NOT_OWNED");
        /// @dev As the StakingPositionManager is the NFT contract, we verify that this ID has been created from this StakingPositionService
        require(msg.sender == stakingPerTokenId[tokenId], "WRONG_STAKING");
    }
```


we can see that the stakingPositionManager's compliance check functions are underlying core functions of the major staking operations of deposit and claim  of staking .

However we take a closer look at the code , the code only executes if the executor is the owner of token id .
it will revert even if the executor is the approved user of the token owner.

```solidity
# checkTokenFullCompliance

require(receiver == ownerOf(tokenId), "TOKEN_NOT_OWNED");
        
# checkIncreaseDepositCompliance

require(receiver == ownerOf(tokenId), "TOKEN_NOT_OWNED");
        
````

as stated , the receiver parameter is not something that is taken from the user upon function invocation , rather its' called with `msg.sender is the receiver param` which effectively only allows the token owner to manage their investment. 


**Attachments**
N/A

1. **Proof of Concept (PoC) File**

However , The current implementation is not practical in real world. In real world , The wealthy owners don't have enough time to do everything on their own.

There is this wealthy investor/Token owner, the will hire bunch of traders or account managers who will manage their assets for them ( the token owner approving them of their tokens instead of just giving away their private keys )

Now this is the case for majority of the token holders that they have approved addresses that take part in portfolio management and investment decisions .

However , the staking functionality does not serve that majority of the crypto holders to take part and eventually lose a lot of share that it could process by allowing the token approved addresses 


2. **Revised Code File (Optional)**
Instead of checking for

```solidity
require(receiver == ownerOf(tokenId), "TOKEN_NOT_OWNED");
        
```

The code should check if the user is either approved address of the token Owner or the token owner itself. In both cases , the transaction should succeed. This will ensure that the staing functionality is available for 60% users that might not have been able to use te previous implementation due to strict ownership checks and owners not having enough time to do everything on their own.

```solidity
require(receiver == approvedOrOwner(tokenId), "TOKEN_NOT_OWNED_NOR_Approved");
        
```
