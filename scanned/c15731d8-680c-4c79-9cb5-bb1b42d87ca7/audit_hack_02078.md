# [C] 6.1 Reentrancy Can Drain Money

## Summary
Severity: Critical
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Security Critical Version 1 Code Corrected

The HoprChannels smart contract uses the ERC777 HoprToken to settle payments. The ERC777 token
allows reentrancies during the transfer via sender and receiver hooks. An attacker can utilize this
reentrancy to drain the balance of HoprChannels contract. One of the places where this can happen is in
the finalizeChannelClosure function.

We describe a more elaborate attack and a straightforward attack.

Attack setup: Alice and Bob cooperate. They have created channels between them, Alice has called
initiateChannelClosure for her channel with Bob, that holds 100 tokens. Bob has valid and yet
unclaimed ticket for 75 tokens. Closure time has passed for the Alice owned channel. Alice has a smart
contract registered for ERC777 hook. Bob is smart contracts that is registered in the ERC1820 registry
for the ERC777 hooks.

- Alice calls finalizeChannelClosure with Bob as destination.
- During the call token.transfer(Alice, 100); in this function, Alice contract gets called.
    - Alice contract calls to Bob contract.
       - Bob contract calls the redeemTicket with valid unclaimed ticket.
          - Channel (Alice, Bob) is spending and (Bob, Alice) is earning.
          - Balance of (Alice, Bob) is decreased by 75. Since the balance of the channel is
             still 100, the new value will be 25.
          - Balance of (Bob, Alice) is increased by 75.
          - Function redeemTicket returns.
       - The Bob contract execution returns to Alice


- Alice contract returns finalizeChannelClosure call.
- The execution continues after the call token.transfer(Alice, 100);
- The balance (25 tokens) of Alice owned channel is nullified with delete and the status is set to the
CLOSED.

As a result of above described schema, the initial 100 tokens of (Alice, Bob) channel will be payed out to
Alice, and in addition Bob will get 75 tokens from his ticket claim. Thus instead of 100 tokens 175 tokens
were withdrawn.

The straightforward attack would be to reenter multiple time into the finalizeChannelClosure as the
state variables are changed after the reentrancy possibility. As a general rule, all state dependent
operations should be done before the possible reentrancy. Additionally, reentrancies could be completely
blocked if not needed.

Code corrected:

In functions that perform transfers of HOPRToken the transfer operations are moved to the end of the
functions.
