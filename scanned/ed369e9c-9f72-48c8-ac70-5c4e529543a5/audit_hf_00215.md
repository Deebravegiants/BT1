# [M] _notSameBlock

## Summary
Severity: Medium
Contest weight: 0.4463
Dataset id: 1117
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The function bondToAccount() of Bonding.sol has a check based on _notSameBlock() _notSameBlock() makes sure the same msg.sender cannot do 2 actions within the same block.

However this can be circumvented in this case: Suppose you call bondToAccount() via a (custom) smart contract, then the msg.sender will be the address of the smart contract. For a pseudo code proof of concept see below.

I’m not sure what the deeper reason is for the _notSameBlock() in bondToAccount(). But if it is important then circumventing this check it will pose a risk.

## Proof of Concept
call function attack1.attack()
    
```solidity
contract attack1 {
   function attack(address account, uint256 amount) {
         call attack2.forward(account, amount);
         call any other function of malt
  }
}

contract attack2 {
   function forward(address account, uint256 amount) {
       call bonding.bondToAccount(account, amount); // uses msg.sender of attack2
   }
}

function bondToAccount(address account, uint256 amount) public {
    if (msg.sender != offering) {
         _notSameBlock();
    }
    ...

function _notSameBlock() internal {
    require( block.number > lastBlock[_msgSender()],"Can't carry out actions in the same block" );
    lastBlock[_msgSender()] = block.number;
}
```

## Recommendation
Add access controls to the function bondToAccount() An end-user could still call bond()

`notSameBlock` is effectively being used as the `nonReentrant` modifier, without the same security guarantees, as such, in spite of not having a specific attack vector, because the warden showed how to side step this security feature of the protocol, am going to raise the severity to Medium
