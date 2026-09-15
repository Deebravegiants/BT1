# [H] `LiquidityPool` contract can not receive `T-NFT` or ERC721 NFTs

## Summary
Severity: High
Chain: Smart contract
Component: ether-fi
Published: 2023-11-07
Source: https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/issues/21
Type: hats-finding

## Details
**Github username:** @0xRizwan
**Submission hash (on-chain):** 0x39e514a238fb38463ea1d7d1656c12a067c40fe174df2d6d278a6f3c5a360acf
**Severity:** high

**Description:**
**Description**\
In `LiquidityPool.sol`, `batchRegisterAsBnftHolder()` function is used BNFT players to register validators they have deposited. This function triggers a 1 ETH transaction to the beacon chain. 

The actual issue is explained below(*only relevant code is kept for simpler understanding of issue by readers/reviewers*)

```Solidity
File: src/LiquidityPool.sol

    function batchRegisterAsBnftHolder(
        bytes32 _depositRoot,
        uint256[] calldata _validatorIds,
        IStakingManager.DepositData[] calldata _registerValidatorDepositData,
        bytes32[] calldata _depositDataRootApproval,
        bytes[] calldata _signaturesForApprovalDeposit
    ) external whenNotPaused {

       // some code

        stakingManager.batchRegisterValidators(_depositRoot, _validatorIds, msg.sender, address(this), _registerValidatorDepositData, msg.sender);
        
       // some code

        }
    }
```

Under the hood, this function calls `stakingManager.batchRegisterValidators()` which is used to create validator object, mints NFTs, sets NB variables and deposits 1 ETH into beacon chain and it can be seen as below,

```Solidity
File: src/StakingManager.sol

    function batchRegisterValidators(
        bytes32 _depositRoot,
        uint256[] calldata _validatorId,
        address _bNftRecipient,
        address _tNftRecipient,
        DepositData[] calldata _depositData,
        address _staker
    ) public whenNotPaused nonReentrant verifyDepositState(_depositRoot) {

       // some code

        for (uint256 x; x < _validatorId.length; ++x) {
            _registerValidator(_validatorId[x], _bNftRecipient, _tNftRecipient, _depositData[x], _staker, 1 ether);
        }
    }
```

To be noted here, `_tNftRecipient` is `liquidityPoolContract` and this is referred as `address(this) in `LiquidityPool.batchRegisterAsBnftHolder()` at L-321.


`_registerValidator()` used `batchRegisterValidators()` also mints NFTS to recipient addressess.

```Solidity
File: src/StakingManager.sol

        // Let validatorId = nftTokenId
        uint256 nftTokenId = _validatorId;
        TNFTInterfaceInstance.mint(_tNftRecipient, nftTokenId);
        BNFTInterfaceInstance.mint(_bNftRecipient, nftTokenId);
```

Here, `T-NFT` is being minted to `_tNftRecipient` which in our case is `liquidityPoolContract`.

The issue here is `liquidityPoolContract` can not received the ERC721 NFTs. `T-NFT` is an ERC721 token which can not be received by `liquidityPool.sol` Contract since it does not support `onERC721Received` method to recieve such tokens.

When the `batchRegisterAsBnftHolder()` function will be called, it will always revert with error `ERC721InvalidReceiver` and this can be checked in RemixIDE.

This is categorised as High severity as core functionality of etherFi contracts will be bricked which could result in redeployment of LiquidityPool contract.

**Attack Scenario**\
When the batchRegisterValidators() is called by BNFT player, it will always revert as the minting of `T-NFT` will always revert due non-support of ERC721 token in `LiquidityPool` contract. This will always revert while permanently freezing/ breaking the core functionality of etherFi contracts.

**Attachments**

1. **Proof of Concept (PoC) File**


https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/blob/180c708dc7cb3214d68ea9726f1999f67c3551c9/src/LiquidityPool.sol#L321


https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/blob/180c708dc7cb3214d68ea9726f1999f67c3551c9/src/StakingManager.sol#L156

https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/blob/180c708dc7cb3214d68ea9726f1999f67c3551c9/src/StakingManager.sol#L391C29-L391C29

2. **Revised Code File (Optional)**
This issue can be resolved by adding the ERC721 token support to `LiquidityPool` contract.

Since the contracts has used openzeppelin library with version 4.8.2 as verified from package.json. Therefore openzeppelin's `ERC721HolderUpgradeable.sol` can be used to mitigate this issue as this contract consists of `onERC721Received()` function to check the ERC721 support and this can be checked below,

```Solidity

    function onERC721Received(
        address,
        address,
        uint256,
        bytes memory
    ) public virtual override returns (bytes4) {
        return this.onERC721Received.selector;
    
```

Below are high level changes should be made to resolve the issue,

```diff
+ import "@openzeppelin-upgradeable/contracts/token/ERC721/utils/ERC721HolderUpgradeable.sol";


- contract LiquidityPool is Initializable, OwnableUpgradeable, UUPSUpgradeable, ILiquidityPool {

+contract LiquidityPool is Initializable, OwnableUpgradeable, ERC721HolderUpgradeable, UUPSUpgradeable, ILiquidityPool {




   // some code



    function initialize(address _eEthAddress, address _stakingManagerAddress, address _nodesManagerAddress, address _membershipManagerAddress, address _tNftAddress) external initializer {
        if (_eEthAddress == address(0) || _stakingManagerAddress == address(0) || _nodesManagerAddress == address(0) || _membershipManagerAddress == address(0) || _tNftAddress == address(0)) revert DataNotSet();
        
        __Ownable_init();
        __UUPSUpgradeable_init();
+      __ERC721Holder_init;

        eETH = IeETH(_eEthAddress);
        stakingManager = IStakingManager(_stakingManagerAddress);
        nodesManager = IEtherFiNodesManager(_nodesManagerAddress);
        membershipManager = IMembershipManager(_membershipManagerAddress);
        tNft = ITNFT(_tNftAddress);
    }
```

Now after applying the above recommendation, T-NFT can be received by LiquidityPool contract.

Note: The import path from openzeppelin must be rechecked as it might differ with different version. Above mitigation is shown for general understanding.
