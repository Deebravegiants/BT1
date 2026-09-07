# [M] # Attackathon _ Fuel Network 32884 - [Smart Contract - Medium] Compilerstd-lib storage collison betwee

## Summary
Severity: Medium
Chain: Smart contract
Component: Fuel Network | Attackathon
Source: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/Fuel%20Network%20%7C%20Attackathon/Attackathon%20_%20Fuel%20Network%2032884%20-%20%5BSmart%20Contract%20-%20Medium%5D%20Compilerstd-lib%20storage%20collison%20between%20variables%20and%20StorageMap%20allows%20hidden%20backdoors%20likely%20loss%20of%20funds.md
Type: immunefi-boost

## Details
Target: https://github.com/FuelLabs/sway/tree/v0.61.2

## Description

## Brief/Intro

Storage layout is a critical component of a smart contract language such as Sway. Unfortunately the language uses different schemes for defining storage slots for simple variables and storage containers, that can lead to different storage variables accessing the same storage. This can lead to malicious users crafting contracts with undetectable backdoors and luring users to interacting with them -- with consequent loss of funds.

## Preliminary Discussion

I would like to start by stating that mixing different strategies for allocating storage slots is incredibly (maybe surprisingly) dangerous, and hard to be done safely.

For both securely developing smart contracts, and trusting smart contracts developed by others, users need to be sure the behavior of contracts compiled using the Sway Language is predictable.

**In particular use of the various&#x20;**_**standard**_**&#x20;features of the Language, or&#x20;**_**standard**_**&#x20;libraries shouldn't cause storage collisions with unpredictable consequences. An auditor looking at a contract that only uses&#x20;**_**standard**_**&#x20;elements should have the ability tell whether a backdoor exists in the contract based on information contained in the source code.**

Unfortunately, the mixing of different strategies for allocating storage slots, as we will see, makes it in many cases impossible to tell a contract containing a secret backdoor introduced by the developer. Conversely introducing such a backdoor is easy for a malicious user.

Currently, the Sway Language uses various different schemes for allocating slots:

1. Directly with user-defined slots, through the keyword `in`.
2. For simple variables by hashing the fully qualified name. E.g. `sha256("storage::namespace.variable")`.
3. For `StorageVector`'s length by hashing the field id obtained in (2).
4. For `StorageVector`'s elements, by adding an offset to the field id obtained in (2). E.g. `sha256("storage.my_vector") + 100u64`.
5. For `StorageVector`'s _nested storage containers_ by hashing the field id prefixed by the index. E.g. `sha256(1u64, sha256("storage.my_vector"))`.
6. For `StorageMap`'s elements, by hashing the field id prefixed by the key. E.g. `sha256(1u64, sha256("storage.my_map"))`.
7. For `admin` (`sway-lib`) by using directly the bits of the address/contract id as the slot.
8. For `owner` (`sway-lib`) by using `sha256("owner")`.

There are a few known issues with the above:

a. While (1) is obviously dangerous (and I believe shouldn't be part of the language or at least its use discouraged), it's mere presence in a code base is likely a red flag, unless it's part of a very well known standard. In that sense, while it certainly can be used to insert a backdoor into a contract, the possibility will be obvious to anyone reading the code.

b. The issue previous reported during the Attackathon, with collisions between (7) and (6) -- report number 32854.

**However these aren't the only problems.**

Note that it is not at all obvious that the various schemes above don't produce collisions -- or even how to ascertain they do or don't.

_Trimmed to 38 lines — full report: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/Fuel%20Network%20%7C%20Attackathon/Attackathon%20_%20Fuel%20Network%2032884%20-%20%5BSmart%20Contract%20-%20Medium%5D%20Compilerstd-lib%20storage%20collison%20between%20variables%20and%20StorageMap%20allows%20hidden%20backdoors%20likely%20loss%20of%20funds.md_
