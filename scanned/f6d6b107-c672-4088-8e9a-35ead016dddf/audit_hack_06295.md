# [H] First deposit fails because initial debt is negative

## Summary
Severity: High
Reporter: hickuphh3
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L269
Type: audit-issue

## Details
# First deposit fails because initial debt is negative

## Summary
Before the first debt mint is performed, the initial `debt` returned will be negative after the first deposit. Converting between signed and unsigned integers reverts if the input is negative, thus causing the deposit to always fail.

## Vulnerability Detail
The 1st `register_deposit()` call will perform `deposit_underlying()` to transfer WETH into the alchemist. Following which, it calls `_calculate_amount_to_mint()` to see how much debt can be minted.

The current debt amount is fetched in `_calculate_max_mintable_amount()`
```vyper
current_debt: uint256 = convert(IAlchemist(self.alchemist).accounts(self)[0], uint256)`
```

However, since no debt has been minted yet, `current_debt` returns a negative value. [As a result, converting it to `uint256` reverts](https://docs.vyperlang.org/en/stable/types.html#type-conversions).

## POC
I copied over the contracts to a new foundry X vyper repo using https://github.com/0xKitsune/Foundry-Vyper and setup mainnet forking. 

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
    IAlchemistV2 alchemist = IAlchemistV2(0x062Bf725dC4cDF947aa79Ca2aaCCD4F385b13b5c);
    IWhitelist whitelist = IWhitelist(0xA3dfCcbad1333DC69997Da28C961FF8B2879e653);
    address yieldToken = 0xa258C4606Ca8206D8aA700cE2143D7db854D168c;
    IERC20 weth = IERC20(0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2);
    // pranking from big WETH holder
    address admin = 0x2fEb1512183545f48f6b9C5b4EbfCaF49CfCa6F3;

    function setUp() public {
        vm.startPrank(admin);
        nft = new FairFundingToken();
        /// @notice: I modified vault to take in admin as a parameter
        /// because of pranking issues => setting permissions
        vault = IVault(
            vyperDeployer.deployContract("Vault", abi.encode(address(nft), admin))
        );
        // to avoid having to repeatedly cast to address
        address vaultAdd = address(vault);
        vault.add_depositor(admin);
        vault.set_alchemist(address(alchemist));

        // whitelist vault in Alchemist system
        vm.stopPrank();
        vm.prank(0x9e2b6378ee8ad2A4A95Fe481d63CAba8FB0EBBF9);
        whitelist.add(vaultAdd);

        vm.startPrank(admin);

        // check yield token is whitelisted
        assert(alchemist.isSupportedYieldToken(yieldToken));

        // mint a few tokens to self
        for (uint i; i < 5; ++i) {
            nft.mint(admin, i);
        }

        // give max WETH approval to vault
        weth.approve(vaultAdd, type(uint256).max);
    }

    function testDepositUnderlying() public {
        weth.transfer(address(this), 10e18);

        vm.stopPrank();
        vm.prank(0x9e2b6378ee8ad2A4A95Fe481d63CAba8FB0EBBF9);
        whitelist.add(address(this));

        weth.approve(address(alchemist), type(uint256).max);
        alchemist.depositUnderlying(
            yieldToken,
            1e18,
            admin,
            1
        );

        int256 debt;
        address[] memory depositedTokens;
        (debt, depositedTokens) = alchemist.accounts(admin);
        // this will be negative
        console.logInt(debt);
    }
}
```

Here's an actual deposit showing how the debt is negative initially, before minting.
<img width="504" alt="image" src="https://user-images.githubusercontent.com/87458768/219265435-db2c2a85-ad15-41d2-bca2-bcd80ed6aa69.png">

## Impact
The first deposit will always revert.

## Code Snippet
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L269

## Tool used
Foundry, Mainnet Forking, Manual Review

## Recommendation
The bigger question here is that as repayments can be both automatic (from strategies) or manual, the debt amount becomes less negative over time.  

Consider how to handle the case where debt is negative.
