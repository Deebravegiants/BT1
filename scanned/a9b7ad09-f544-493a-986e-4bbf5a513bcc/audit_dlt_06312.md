# [M] In the event of a hardfork, IncentivizedMockImplementation is susceptible to cross-chain signature replay

## Summary
Severity: Medium
Chain: Smart contract
Component: Catalyst-Exchange
Published: 2024-01-31
Source: https://github.com/hats-finance/Catalyst-Exchange-0x3026c1ea29bf1280f99b41934b2cb65d053c9db4/issues/69
Type: hats-finding

## Details
**Github username:** @PlamenTSV
**Twitter username:** @p_tsanev
**Submission hash (on-chain):** 0xa099d3d13dfa2619ab793bf91a79614b1f71b35c5be5b169264a17ed98f580bb
**Severity:** medium

**Description:**
**Description**\
Both the incentivized mock and wormhole implementation implement methods to send, sign and verify packets of messages. Messages which, upon submission, get signed by the owner/signer of the implementation against their identifiers which include: block number, destination identifier and the message itself, as well as a chainId(on the wormhole) or a SOURCE_IDENTIFIER(on the mock). Due to the SOURCE_IDENTIFIER being hardcoded, with no method to alter it, a hardfork of the chain would leave the contract open for cross-chain replay of old messages.

**Attack Scenario**\
A hardfork/split in the word software and blockchains is described as "...a protocol software upgrade that permanently splits a blockchain network into two separate chains. It occurs when nodes on the newest version of the protocol fail to accept the older version of the blockchain."
It an unusual occurence that leads to the seperation of the chain at a given block, producing 2 different block-chains. 
The Wormhole implementation would suffer no change, because it uses ``chainId()``  to encode identifiers, which changes with forks. Unlike it however, the SOURCE_IDENTIFIER does not change, so identical messages on the 2 different chains would be signed with the same parameters, leading to the same metadata, that later decoded would approve the signature on both chains, allowing the messages to be replayed cross-chain.
Hardforks are often unpredictable events, and their occurence/likelihood could either low or medium depending on the future EIPs, but the impact is definitely high, thus - MEDIUM

More on previous hardforks, solidifying their unpredictiveness and inevitable occurence with more incoming EIPs: https://coinloan.io/blog/history-of-ethereum-hard-forks/
Historical issues with signatures: 
https://solodit.xyz/issues/m-05-replay-attack-in-case-of-hard-fork-code4rena-golom-golom-contest-git
https://solodit.xyz/issues/m-24-oracles-are-vulnerable-to-cross-chain-replay-attacks-sherlock-none-gmx-git

**Attachments**

1. **Proof of Concept (PoC) File**
<!-- You must provide a file containing a proof of concept (PoC) that demonstrates the vulnerability you have discovered. -->

2. **Revised Code File (Optional)**
<!-- If possible, please provide a second file containing the revised code that offers a potential fix for the vulnerability. This file should include the following information:
- Comment with a clear explanation of the proposed fix.
- The revised code with your suggested changes.
- Any additional comments or explanations that clarify how the fix addresses the vulnerability. -->

Recommendation: add an admin function for changing the SOURCE_IDENTIFIER in the mock or just use chainId() like on wormhole, as it is foulproof.
