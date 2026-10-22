# [M] 6.2 Inconsistent States and Events

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Code Corrected

Functions using ERC777 transfers can be reentered (a reentrancy does not necessarily need to happen
in the same function but in another relevant function in the system.). Some of these functions have a
code after the possible reentrancy point. This might become problematic if the logic relies on state
variables like in finalizeChannelClosure, redeemTicket. Besides the more critical reentrancy
issue we mentioned, these function's events might be inconsistent or misleading.

For example, in redeemTicket event ChannelUpdate is emitted. This event uses
spendingChannel storage variable. Given the redeemTicket is called and the ERC777 hook is used
to change any storage variable used in these events, the events can emit inconsistent information. This
can be done if during the transfer, the hook calls the bumpChannel in between.

The same applies to the other places where logic after the reentrancy possibility relies on state variables.
We do not know if the client's or third party software will rely on these events. If so, the severity of the
issue would be affected.

Code corrected:

In functions that perform transfers of HOPRToken the transfer operations are moved to the end of the
functions.
