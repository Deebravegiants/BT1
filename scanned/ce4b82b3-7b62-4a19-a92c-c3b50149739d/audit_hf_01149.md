# [M] A user might lose ETH when sending a deposit in a multicall that includes a depositOnBehalf call

## Summary
Severity: Medium
Reporter: mt030d
Contest weight: 0.6779
Dataset id: 4905
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The executeDeposit function in the Deposit library underlies both the Size.deposit and Size.depositOnBehalfOf functions. A code branch `if (msg.value > 0) {...}` in executeDeposit wraps the caller's sent ETH into WETH, which is then deposited into the Size market.
```solidity
function executeDeposit(State storage state, DepositOnBehalfOfParams memory externalParams) public {
// ...
    if (msg.value > 0) {
        // do not trust msg.value (see `Multicall.sol`)
        amount = address(this).balance;
        // slither-disable-next-line arbitrary-send-eth
        state.data.weth.deposit{value: amount}();
        state.data.weth.forceApprove(address(this), amount);
        from = address(this);
    }
// ...
}
```
This design likely aims to facilitate deposits without requiring the depositor to first wrap their ETH into WETH. However, in a depositOnBehalfOf call, it should not be the operator's ETH that is deposited; instead, the authorizer's WETH should be deposited. Typically, the operator would not call depositOnBehalfOf with a non-zero msg.value. However, this can happen in a multicall context. For example, Alice authorizes Bob as the operator and wants him to deposit 100 WETH into Size on her behalf. Meanwhile, Bob, also a Size user, wants to deposit 100 ETH as collateral. Bob bundles these two transactions into a multicall and sends it on-chain. In the multicall, the depositOnBehalfOf tx sees a non-zero msg.value and uses Bob's ETH in the deposit. The following deposit call would deposit zero amount since the msg.value is used previously. As a result, Bob's 100 ETH is deposited as Alice's collateral (shown in the following proof of concept section), which is not what Bob intended.

Impact Explanation:
High - The operator could lose the ETH sent to deposit() without receiving the collateral token they should get.

## Proof of Concept
```solidity
pragma solidity 0.8.23;
import {Action, Authorization} from "@src/factory/libraries/Authorization.sol";
import {DepositOnBehalfOfParams, DepositParams} from "@src/market/libraries/actions/Deposit.sol";
import {BaseTest, Vars} from "@test/BaseTest.sol";
import {console} from "forge-std/Test.sol";
contract PoCTest is BaseTest {
    function setUp() public override {
        super.setUp();
        _mint(address(weth), alice, 100e18);
        _approve(alice, address(weth), address(size), type(uint256).max);
        vm.deal(bob, 100e18);
        vm.prank(alice);
        sizeFactory.setAuthorization(bob, Authorization.getActionsBitmap(Action.DEPOSIT));
    }

    function test_OperatorLossMsgValue() public {
        assertTrue(sizeFactory.isAuthorized(bob, alice, Action.DEPOSIT));
        console.log("============= Initial state ============================");
        {
            Vars memory state = _state();
            console.log("Alice's collateralToken balance: ", state.alice.collateralTokenBalance);
            console.log("Alice's weth balance: ", weth.balanceOf(alice));
            console.log("Bob's collateralToken balance: ", state.bob.collateralTokenBalance);
            console.log("Bob's eth balance: ", bob.balance);
        }

        uint256 snapshot = vm.snapshotState();
        console.log("============= Situation 1: txs are sent separately ============");
        vm.prank(bob);
        size.depositOnBehalfOf(
            DepositOnBehalfOfParams({
                params: DepositParams({token: address(weth), amount: 100e18, to: alice}),
                onBehalfOf: alice
            })
        );
        vm.prank(bob);
        size.deposit{value: 100e18}(DepositParams({token: address(weth), amount: 100e18, to: bob}));
        {
            Vars memory state = _state();
            console.log("Alice's collateralToken balance: ", state.alice.collateralTokenBalance);
            console.log("Alice's weth balance: ", weth.balanceOf(alice));
            console.log("Bob's collateralToken balance: ", state.bob.collateralTokenBalance);
            console.log("Bob's eth balance: ", bob.balance);
        }

        vm.revertTo(snapshot);
        console.log("============= Situation 2: txs are sent in multicall ============");
        bytes[] memory txs = new bytes[](2);
        txs[0] = abi.encodeCall(
            size.depositOnBehalfOf,
            (
                DepositOnBehalfOfParams({
                    params: DepositParams({token: address(weth), amount: 100e18, to: alice}),
                    onBehalfOf: alice
                })
            )
        );
        txs[1] = abi.encodeCall(size.deposit, (DepositParams({token: address(weth), amount: 100e18, to: bob})));
        vm.prank(bob);
        size.multicall{value: 100e18}(txs);
        {
            Vars memory state = _state();
            console.log("Alice's collateralToken balance: ", state.alice.collateralTokenBalance);
            console.log("Alice's weth balance: ", weth.balanceOf(alice));
            console.log("Bob's collateralToken balance: ", state.bob.collateralTokenBalance);
            console.log("Bob's eth balance: ", bob.balance);
        }
    }
}
```
Place the above code in foundry test folder. The test result is as follows:
```
[PASS] test_OperatorLossMsgValue() (gas: 1106746)
Logs:
============= Initial state ============================
Alice's collateralToken balance: 0
Alice's weth balance: 100000000000000000000
Bob's collateralToken balance: 0
Bob's eth balance: 100000000000000000000

============= Situation 1: txs are sent separately ============
Alice's collateralToken balance: 100000000000000000000
Alice's weth balance: 0
Bob's collateralToken balance: 100000000000000000000
Bob's eth balance: 0

============= Situation 2: txs are sent in multicall ============
Alice's collateralToken balance: 100000000000000000000
Alice's weth balance: 100000000000000000000
Bob's collateralToken balance: 0
Bob's eth balance: 0
```

## Recommendation
Consider rewriting the deposit and depositOnBehalfOf functions to decouple depositOnBehalfOf from msg.value related logic.
