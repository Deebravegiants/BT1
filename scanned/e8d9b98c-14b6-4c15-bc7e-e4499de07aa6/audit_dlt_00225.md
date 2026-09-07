# [M] CL-2020-26: Unlimited gossip RPC size

## Summary
Severity: Medium
Chain: Ethereum (consensus layer)
Component: Teku
Published: 2021-12-01
Source: https://github.com/ethereum/public-disclosures/blob/master/disclosures/CL-2021-12-01.md
Type: ef-disclosure

## Details
# Teku/JVM-libp2p Gossip DoS

Found in the past week by @protolambda, there are several issues that need to be addressed to protect against DoS risks:
* [1] OOM: Unlimited gossip subscriptions info retained in memory
* [2] OOM/CPU DoS: Unlimited gossip RPC size
  * general DoS vector
  * example with pubsub messages
* [3] On-demand CPU delays: Hashmap attack, crafted 56000 gossip 6-byte pre-images to same hashCode.
  - hashset operation on subscriptions
  - hashset operation on published messages
  - misc., e.g. control messages, or the topic IDs list in publish-list item (onNewMessage)
* [4] Questions about lossy IDs

**Notes:**
- Often I refer to "RPC" here, this is the "RPC" type in the gossip protobuf typing, a type containing everything known in gossipsub.
- Some issues are more systemic with gossipsub, be cautious with anything while other clients implement fixes for their issues (related, although not the same).


## [1] OOM: Unlimited gossip subscriptions info retained in memory

This is an older attack, first discovered in Prysm and Lighthouse, disclosed with libp2p, and then forgotten about. However, it still appears to be applicable to Teku:
- Any subscription topic is accepted (no subscriptions filter)
- Any amount of subscriptions is allowed
- Known subscriptions of peers, even if not interesting, are retained in memory indefinitely.
- No scoring or RPC message rate limiting, peer are free to repeat as fast as they can.

Now, to cause an OOM:
- Attacker crafts a big message (say, 1 MB, within normal looking limit)
- It contains 300.000+ subscription items, 3 bytes each (just an integer encoded as bytes or string)
- These are all registered for the peer. Every 3 byte message may have a 30+ byte overhead in JVM (pointers, lengths, type, hashcode object header, hashmap structure, etc.).
- Rinse and repeat, attacker sends 500 MB worth of subscriptions, to fill 5 GB of memory, and force an OOM.
  - On my "small" 8 GB ram laptop, a sudden 2 GB increase may already be enough, and take just 200 MB, or 200 fully "valid" RPC messages
- As long as info is not pruned (might happen on disconnect, not verified), the attacker can take their time to keep filling memory.

The problem is exploited from `onInbound`, the first thing is (See [here](https://github.com/libp2p/jvm-libp2p/blob/eb0303a85d8109e020e2f2690ad393a38efe289c/src/main/kotlin/io/libp2p/pubsub/AbstractRouter.kt#L292)):
```kotlin
msg.subscriptionsList.forEach { handleMessageSubscriptions(peer, it) }

```

_Trimmed to 38 lines — full report: https://github.com/ethereum/public-disclosures/blob/master/disclosures/CL-2021-12-01.md_
