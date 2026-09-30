# [M] Both block.prevrandao and

## Summary
Severity: Medium
Contest weight: 0.4306
Dataset id: 1713
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Both block.prevrandao and block.timestamp are not reliably source of randomness.
In the ERC20Incentive.sol,
```solidity
function drawRaffle() external override onlyOwner {
    if (strategy != Strategy.RAFFLE) revert BoostError.Unauthorized();
    LibPRNG.PRNG memory _prng = LibPRNG.PRNG({state: block.prevrandao + block.timestamp});
    address winnerAddress = entries[_prng.next() % entries.length];
    asset.safeTransfer(winnerAddress, reward);
    emit Claimed(winnerAddress, abi.encodePacked(asset, winnerAddress, reward));
}
```
the code use block.prevrandao and block.timestamp as source of randomness to determine who is lucky to win the raffle.
However, both op code are not good source of randomness.
https://eips.ethereum.org/EIPS/eip-4399
Security Considerations The PREVRANDAO (0x44) opcode in PoS Ethereum (based on the beacon chain RANDAO implementation) is a source of randomness with different properties to the randomness supplied by BLOCKHASH (0x40) or DIFFICULTY (0x44) opcodes in the PoW network.
Biasability The beacon chain RANDAO implementation gives every block proposer 1 bit of influence power per slot. Proposer may deliberately refuse to propose a block on the opportunity cost of proposer and transaction fees to prevent beacon chain randomness (a RANDAO mix) from being updated in a particular slot.
Miner can manipulate the block.prevrandao and block.timestamp to let specific address win the raffle

## Recommendation
change random generate method (can use chainlink VRF, etc...)
