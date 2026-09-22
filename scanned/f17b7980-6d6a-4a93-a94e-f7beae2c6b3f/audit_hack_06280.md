# [H] Unmarked loan repayments for existing token holders is unfairly distributed to new deposits

## Summary
Severity: High
Reporter: hickuphh3
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L198-L232
Type: audit-issue

## Details
# Unmarked loan repayments for existing token holders is unfairly distributed to new deposits

## Summary
New depositors are included in unclaimed / unmarked yield distribution when it should only be split among existing current token holders.
 
## Vulnerability Detail
Existing unmarked WETH yield (yield that haven't been marked claimable) isn't claimed whenever a new deposit occurs: yield can only be marked claimable through the external function `withdraw_underlying_to_claim()`. This means that new depositors are entitled to the unmarked yield as well, when it shouldn't be the case.

## POC
Refer to the `testClaimableYieldAmountsWithNewDeposits()` test case below. Note that I used foundry to enable this test.

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.18;

import "forge-std/Test.sol";
import "../../lib/utils/VyperDeployer.sol";

import "../IVault.sol";
import "../IAlchemistV2.sol";
import "../MintableERC721.sol";
import "openzeppelin/token/ERC20/IERC20.sol";

contract VaultTest is Test {
    ///@notice create a new instance of VyperDeployer
    VyperDeployer vyperDeployer = new VyperDeployer();

    FairFundingToken nft;
    IVault vault;
    address vaultAdd;
    IAlchemistV2 alchemist = IAlchemistV2(0x062Bf725dC4cDF947aa79Ca2aaCCD4F385b13b5c);
    IWhitelist whitelist = IWhitelist(0xA3dfCcbad1333DC69997Da28C961FF8B2879e653);
    address yieldToken = 0xa258C4606Ca8206D8aA700cE2143D7db854D168c;
    IERC20 weth = IERC20(0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2);
    // pranking from big WETH holder
    address admin = 0x2fEb1512183545f48f6b9C5b4EbfCaF49CfCa6F3;
    address user1 = address(0x123);
    address user2 = address(0x456);
    
    function setUp() public {
        vm.startPrank(admin);
        nft = new FairFundingToken();
        /// @notice: I modified vault to take in admin as a parameter
        /// because of pranking issues => setting permissions
        vault = IVault(
            vyperDeployer.deployContract("Vault", abi.encode(address(nft), admin))
        );
        // to avoid having to repeatedly cast to address
        vaultAdd = address(vault);
        vault.set_alchemist(address(alchemist));

        // whitelist vault and users in Alchemist system, otherwise will run into permission issues
        vm.stopPrank();
        vm.startPrank(0x9e2b6378ee8ad2A4A95Fe481d63CAba8FB0EBBF9);
        whitelist.add(vaultAdd);
        whitelist.add(admin);
        whitelist.add(user1);
        whitelist.add(user2);
        vm.stopPrank();

        vm.startPrank(admin);

        // add depositors
        vault.add_depositor(admin);
        vault.add_depositor(user1);
        vault.add_depositor(user2);

        // check yield token is whitelisted
        assert(alchemist.isSupportedYieldToken(yieldToken));

        // mint NFTs to various parties
        nft.mint(admin, 1);
        nft.mint(user1, 2);
        nft.mint(user2, 3);
        

        // give max WETH approval to vault & alchemist
        weth.approve(vaultAdd, type(uint256).max);
        weth.approve(address(alchemist), type(uint256).max);

        // send some WETH to user1 & user2
        weth.transfer(user1, 10e18);
        weth.transfer(user2, 10e18);

        // users give WETH approval to vault and alchemist
        vm.stopPrank();
        vm.startPrank(user1);
        weth.approve(vaultAdd, type(uint256).max);
        weth.approve(address(alchemist), type(uint256).max);
        vm.stopPrank();
        vm.startPrank(user2);
        weth.approve(vaultAdd, type(uint256).max);
        weth.approve(address(alchemist), type(uint256).max);
        vm.stopPrank();

        // by default, msg.sender will be admin
        vm.startPrank(admin);
    }

    function testClaimableYieldAmountsWithNewDeposits() public {
        uint256 depositAmt = 1e18;
        // Setup: admin performs deposit
        vault.register_deposit(1, depositAmt);
        vm.stopPrank();

        // Simulate yield: someone does partial manual repayment
        vm.prank(user2);
        alchemist.repay(address(weth), 0.1e18, vaultAdd);

        // Take snapshot
        uint256 snapshot = vm.snapshot();

        // Scenario A: No Incoming Deposit
        // Step 1: Mark claimable
        vault.withdraw_underlying_to_claim(
            alchemist.convertUnderlyingTokensToShares(yieldToken, 0.01e18) + 100,
            0.01e18
        );

        // Step 2: See claimable yield amount
        uint256 claimableYieldNoNewDeposit = vault.claimable_for_token(1);

        // Revert to snapshot
        vm.revertTo(snapshot);

        // Scenario B: Incoming Deposit
        // Step 1: User1 does deposit
        vm.prank(user1);
        vault.register_deposit(2, depositAmt);

        // Step 2: Mark claimable
        vault.withdraw_underlying_to_claim(
            alchemist.convertUnderlyingTokensToShares(yieldToken, 0.01e18) + 100,
            0.01e18
        );

        // Step 3: See claimable yield amount
        uint256 claimableYieldWithNewDeposit = vault.claimable_for_token(1);

        // Compare the 2: Expect the yield with new deposit to be lesser
        assertLt(claimableYieldWithNewDeposit, claimableYieldNoNewDeposit);

        // At the same time, User1 unfairly gets yield
        assertGt(vault.claimable_for_token(2), 0);
    }
}
```

## Impact
Existing token holders unfairly have their yield diluted by new deposits.

## Code Snippet
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L198-L232
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L393-L404

## Tool used
Foundry, Mainnet Forking, Manual Review

## Recommendation
Unmarked yield should be marked claimable with every incoming deposit, before `total_shares` is incremented.
