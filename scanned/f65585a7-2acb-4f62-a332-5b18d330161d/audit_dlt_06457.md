# [M] distributeRewards function allows duplicate campaigns to be submitted by the updater

## Summary
Severity: Medium
Chain: Smart contract
Component: Metrom
Published: 2024-05-20
Source: https://github.com/hats-finance/Metrom-0xfdfc6d4ac5807d7460da20a3a1c0c84ef2b9c5a2/issues/19
Type: hats-finding

## Details
**Github username:** @sonny2k
**Twitter username:** --
**Submission hash (on-chain):** 0xfbcbe4889614551e63f2f91b05ab1ad63262d8341abe84ef1103ad7e1c2b1ae6
**Severity:** medium

**Description:**
**Description**\
In [distributeRewards](https://github.com/hats-finance/Metrom-0xfdfc6d4ac5807d7460da20a3a1c0c84ef2b9c5a2/blob/main/src/Metrom.sol#L234), there is no check if `_bundles` array argument has duplicate campaignIds. Therefore, if the updater provides duplicate entries for campaignIds, users from other campaigns may have the chance to claim rewards on the duplicate campaignId which was mistakenly put in by the updater.

**Attack Scenario**
1. The updater decides to distributeRewards for 2 campaigns, for example: campaign 1 and campaign 2.
2.  For somehow the updater, or the system off-chain submitted 2 different root and data but with the same campaignId of 1.
3.  users and campaignOwner from campaign 2 is able to claim the rewards which was distributed for campaign 1.

**Attachments**

1. **Proof of Concept (PoC) File**
copy this test case to test/DistributeRewards.sol to see how duplicate campaign can be submitted

```sol
 function test_successDuplicateCampaigns() public {
        MintableERC20 _mintableErc20 = new MintableERC20("Test", "TST");
        _mintableErc20.mint(address(this), 10.1 ether);
        _mintableErc20.approve(address(metrom), 10.1 ether);
        vm.assertEq(_mintableErc20.balanceOf(address(this)), 10.1 ether);

        address[] memory _rewardTokens = new address[](1);
        _rewardTokens[0] = address(_mintableErc20);

        uint256[] memory _rewardAmounts = new uint256[](1);
        _rewardAmounts[0] = 10 ether;

        CreateBundle memory _createBundle = CreateBundle({
            chainId: 1,
            pool: address(1),
            from: uint32(block.timestamp + 10),
            to: uint32(block.timestamp + 20),
            specification: bytes32(0),
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Metrom-0xfdfc6d4ac5807d7460da20a3a1c0c84ef2b9c5a2/issues/19_
