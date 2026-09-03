# [H] Zeta Observer nodes are not listening to `internal TXs`, which makes Smart Contract Wallets users' funds locked when making `Omnichain calls`.

## Summary
Severity: High
Chain: Smart contract
Component: 2023-11-zetachain
Published: 2023-12-17
Source: https://github.com/code-423n4/2023-11-zetachain-findings/issues/419
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/zetaclient/evm_client.go#L952


# Vulnerability details


## Impact

Zetachain allows omnichain TXs (sending funds from external chains to Zeta EVM chain), using different methods.
- If it's just sending main blockchain coin funds between addresses: You deposit funds directly to the `TSS_ADDRESS` and it will send money to the destination address as ZRC-20 tokens on Zeta EVM chain.
- If you are sending ERC20: You need to use `ERC20Custody::deposit()`.

The problem occurs in the first sending method. When the user sends funds (native chain coins) to the `TSS_ADDRESS`.

To define the receiver address you have two things to do:
- provide it in the data field of the TX in bytes format (+ any additional message if needed), and Observer nodes take out the rest of the job to decode.
- Not providing data field in the TX, and in that case, Observers use the caller itself as the receiver address on the Zeta blockchain.

The problem affects Omnichain (Inbound TXs, external EVM => Zeta EVM) which is made by smart contract wallet users.

When smart contract wallets make a sending request, it doesn't make an RPC call. They are making low-level `call` to transfer funds. And here is where the problem occurs.

Observers will not notice this transaction, funds will be sent to the `TSS_ADDRESS` and the Observers will not know that there is an Omnichain call has happened. So user funds will be locked in the `TSS_ADDRESS`.

**Why Smart Contract Wallets are important?**
We should keep in mind that Smart Contract wallets are heavily adopted, and The problem does not affect a small group of users. Mult-sig wallets are increasing, and Account Abstraction is coming, Users will deal with Smart Contract Wallets in the near future instead of EOA.

This is dangerous for users, as most of the users are using their wallets using a UI, and some popular wallets like MetaMask will support account abstraction soon, which will make users' wallets a Smart Contract Wallet as we illustrated before. So users will not be able to interact with ZetaChain and will lose their funds without knowing what is going wrong.


## Proof of Concept

> In our auditing process of the protocol, we made a lot of things (installing deps, making contracts, writing deployments and interact scripts, etc...), So It will be hard for the judger to set up the development environment.
> We worked on the second part `protocol-contract`, and used zeta_testnet for our testing purposes.
> Here is the Dropbox link to download the `protocol-contract` we worked on, you will find `setup.md` to help you install deps, and run POC scripts easily without any problems.


_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-11-zetachain-findings/issues/419_
