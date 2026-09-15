# [M] Owner is not transferrable

## Summary
Severity: Medium
Reporter: Jeiwan
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/Registry.sol#L14
Type: audit-issue

## Details
# Owner is not transferrable

## Summary
Multiple contracts in the project ([Registry](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/Registry.sol#L14), [Auction](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/AuctionInternal.sol#L24), [Queue](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/QueueInternal.sol#L27), [Vault](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultInternal.sol#L19)) define "owner" role by inheriting from SolidState's `OwnableInternal`. Each of these contracts defines a set of critical functions that can only be called by an owner. To name a few:
1. [setExchangeHelper](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/Queue.sol#L70);
1. [setAuction](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultAdmin.sol#L28);
1. [setAuctionWindowOffsets](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultAdmin.sol#L41);
1. [setDelta64x64](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultAdmin.sol#L64);
1. [setFeeRecipient](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultAdmin.sol#L98);
1. [setKeeper](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultAdmin.sol#L116);
1. [setPricer](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultAdmin.sol#L129);
1. [setQueue](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultAdmin.sol#L142);
1. changing implementations in [QueueProxy](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/QueueProxy.sol#L43) and [AuctionProxy](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/AuctionProxy.sol#L30).

In case current owner is compromised or there's a high risk of its private key being leaked, the whole protocol will be in danger. To mitigate such risks, `OwnableInternal` allows to transfer ownership to a different address. However, neither of the contracts inheriting from it exposes the `_transferOwnership` function. Thus, neither of the contracts can have its owner transferred to a different address in case the current owner was compromised.
## Vulnerability Detail
All the contracts that inherit from SolidState's `OwnableInternal` don't expose the `_transferOwnership` function by implementing an owner-only public function that calls `_transferOwnership`.
## Impact
In case owner is compromised, the protocol is under the highest risk. Some exploit scenarios:
1. owner deploys new implementations of Queue and Auction that send deposits and premium to an attacker's address;
1. owner changes Queue contract address to a malicious contract that mints shares in the Vault and allows attacker to withdraw funds from the Vault (and expired options);
1. owner changes Queue contract address to a malicious contract that sends all deposited funds to an attacker's address;
1. owner changes Auction contract to a malicious contract that sends premium to an attacker's address;
1. owner sets fee recipient address to an attacker's address;
1. owner changes ExchangeHelper address to a contract that sends all tokens to an attacker's address.
## Code Snippet
A `_transferOwnership` exposing function is missed in all the contracts that inherit from `OwnableInternal`.
## Tool used
Manual Review
## Recommendation
Implement a public function (that can only be called by owner) that calls the `_transferOwnership` function from `OwnableInternal` to transfer owner to a different address. It's also recommended to use the 2-step transferring process, e.g. OpenZeppelin's [Ownable2Step](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/access/Ownable2Step.sol).
