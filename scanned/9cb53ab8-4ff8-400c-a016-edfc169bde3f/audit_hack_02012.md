# [M] 6.5 L2 Address Sanity Checks

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Code Corrected

In StarkNet users do not have addresses. Transactions sent to the network have the 0 address as caller.
In order to identify accounts via addresses, each user deploys his account contract and interacts with
contracts such as the DAI token using his account-contract.

- The deposit() function of the L1DAIBridge contract allows users to deposit with the to address
    set to 0. The execution of finalize_deposit initiated by the l1_handler on l2 however will fail as
    minting DAI for the zero address will revert. As a result the deposited DAIs on L1 will be locked in
    the escrow.

Furthermore, note that to will be received as a felt on L2. Hence, the true to address on L2 will be
to % R. Therefore, it could be possible to for example specify address R on L1 which will map to
zero-address (similarly R+1 will map to address 1). Users could be protected from errors by restricting the
allowed address range on L1.

- L2 DAI allows to give approvals specifying the 0 address as caller. All holders of L2 DAI must be
    aware that this is very dangerous and means that anyone crafting an external transaction to the
    network can transfer their DAI using this approval.


- A user could specify the l2_dai contract as the recipient of the funds on deposit. Since the L1 call
    would succeed while the L2 call to the l1_handler would fail, the cross-layer message would remain
    unconsumed.

Code corrected:

The code does the following checks now on L1:

- to != 0 to ensure that the address is non-zero.
- to != l2Dai to prevent a failing mint.
- to < SN_PRIME to prevent a possible StarkNet overflow.
- All functions related to approvals in the l2 DAI contract now forbid approving the zero-address.
