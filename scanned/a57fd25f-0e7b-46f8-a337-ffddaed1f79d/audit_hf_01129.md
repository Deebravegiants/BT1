# [M] Proposals vote weightage doesn't matter due to wrong initialization of proposal Threshold in Governance contract

## Summary
Severity: Medium
Reporter: AngryMustacheMan
Contest weight: 0.7376
Dataset id: 4618
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In Governance contract's constructor, it is clearly seen that proposal threshold is set to 0 in GovernorSettings parameter as shown below:
```solidity
constructor(
    string memory name_,
    IVotes _token,
    TimelockController _timelock
)
    Governor(name_)
    GovernorSettings(7200, 50_400, 0)/* <@audit - proposalThreshold is set to zero here */
    GovernorVotes(_token)
    GovernorVotesQuorumFraction(4)
    GovernorTimelockControl(_timelock)
{
```
Proposal threshold is basically the minimum number of votes needed to propose governance actions is currently set to 0. This configuration essentially allows proposals to be submitted without any voting threshold. It is necessary to establish an appropriate proposal Threshold value that ensures accessibility while preventing spam and low-quality proposals.

Impact Explanation:
1. Any Proposals can be passed as there is no voting threshold to check the number of votes against it.
2. Spamming of low-quality proposals possible.

## Proof of Concept
Add the proof of concept test given below to test/unit/Airlock.t.sol and import the following to the file:
```solidity
import { console } from "forge-std/Test.sol";
import {Governance} from "src/Governance.sol";
import { TimelockController } from "@openzeppelin/governance/TimelockController.sol";
```
Running forge test --match-path test/unit/Airlock.t.sol --mt test_POC -vvv command:
```solidity
/* @audit - my poc start */
function test_POC() public returns (address, address) {
    bytes memory tokenFactoryData =
        abi.encode(DEFAULT_TOKEN_NAME, DEFAULT_TOKEN_SYMBOL, 0, 0, new address[](0), new uint256[](0));
    uint160 sqrtPrice = TickMath.getSqrtPriceAtTick(DEFAULT_START_TICK);
    bytes memory poolInitializerData = abi.encode(
        sqrtPrice,
        DEFAULT_MIN_PROCEEDS,
        DEFAULT_MAX_PROCEEDS,
        DEFAULT_STARTING_TIME,
        DEFAULT_ENDING_TIME,
        DEFAULT_START_TICK,
        DEFAULT_END_TICK,
        DEFAULT_EPOCH_LENGTH,
        DEFAULT_GAMMA,
        false,
        DEFAULT_PD_SLUGS
    );
    (bytes32 salt, address hook, address asset) = mineV4(
        MineV4Params(
            address(airlock),
            address(manager),
            DEFAULT_INITIAL_SUPPLY,
            DEFAULT_INITIAL_SUPPLY,
            address(0),
            tokenFactory,
            tokenFactoryData,
            uniswapV4Initializer,
            poolInitializerData
        )
    );
    (,,address governance,address timelock,) = airlock.create(
        CreateParams(
            DEFAULT_INITIAL_SUPPLY,
            DEFAULT_INITIAL_SUPPLY,
            address(0),
            tokenFactory,
            tokenFactoryData,
            governanceFactory,
            abi.encode(DEFAULT_TOKEN_NAME),
            uniswapV4Initializer,
            poolInitializerData,
            uniswapV2LiquidityMigrator,
            new bytes(0),
            address(0xb0b),
            salt
        )
    );
    address[] memory targets = new address[](1);
    uint256[] memory values = new uint256[](1);
    bytes[] memory calldatas = new bytes[](1);
    string memory description = "";
    // Assign values to the elements
    targets[0] = address(0);
    // address(0) for target
    values[0] = 0;
    // 0 for value
    calldatas[0] = bytes("");
    // empty bytes array for calldata
    console.log("Present Proposal Threshold",Governance(payable(governance)).proposalThreshold());
    vm.warp(block.timestamp + 91 days);
    uint256 proposalId = Governance(payable(governance)).propose(targets,values,calldatas,description);
    console.log("Proposal id returned : ",proposalId);
    return (hook, asset);
}
/* @audit - my poc end */
```
Output:
[] Compiling...
[] Compiling 1 files with Solc 0.8.26
[] Solc 0.8.26 finished in 57.74s
Compiler run successful with warnings:
Warning (2072): Unused local variable.
--> test/unit/Airlock.t.sol:217:30:
|
217 |     (,,address governance,address timelock,)= airlock.create(
|                              ^^^^^^^^^^^^^^^^
Ran 1 test for test/unit/Airlock.t.sol:AirlockTest
[PASS] test_POC() (gas: 24567533)
Logs:
Present Proposal Threshold 0
Proposal id returned : 73289935354017558079201407528452784216240740650700234447014645003792921763461
Suite result: ok. 1 passed; 0 failed; 0 skipped; finished in 772.18ms (45.48ms CPU time)

## Recommendation
Initialize the proposalThreshold with a meaning value to avoid problems.
