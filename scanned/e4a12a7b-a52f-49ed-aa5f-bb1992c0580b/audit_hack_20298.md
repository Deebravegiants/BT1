# [H] 5.1.6 Preservation ofmsg.senderin ZkSync could break certain trust assumption

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** High Risk
**Context:** Any contract deployed on ZkSync that relies onmsg.sender
**Description:** For ZkSync chain, themsg.senderis preserved for L1 -> L2 calls. One of the rules when pursuing a
cross-chain strategy is to never assume that address control between L1 and L2 is always guaranteed. For EOAs
(i.e., non-contract accounts), this is generally true that any account that can be accessed on Ethereum will also be
accessible on other EVM-based chains. However, this is not always true for contract-based accounts as the same
account/wallet address might be owned by different persons on different chains. This might happen if there is a
poorly implemented smart contract wallet factory on multiple EVM-based chains that deterministically deploys a
wallet based on some user-defined inputs.
For instance, if a smart contract wallet factory deployed on both EVM-based chains uses deterministic CREATE
which allows users to define itssaltwhen deploying the wallet, Bob might useABCas salt in Ethereum and Alice
might useABCas salt in Zksync. Both of them will end up getting the same wallet address on two different chains.
A similar issue occurred in the Optimism-Wintermute Hack, but the actual incident is more complicated.
Assume that0xABCis a smart contract wallet owned and deployed by Alice on ZkSync chain. Alice performs a
xcall from Ethereum to ZkSync withdelegateset to0xABCaddress. Thus, on the destination chain (ZkSync), only
Alice's smart contract wallet0xABCis authorized to call functions protected by theonlyDelegatemodifier.


Bob (attacker) saw that the0xABCaddress is not owned by anyone on Ethereum. Therefore, he proceeds to take
ownership of the0xABCby interacting with the wallet factory to deploy a smart contract wallet on the same address
on Ethereum. Bob can do so by checking out the inputs that Alice used to create the wallet previously. Thus, Bob
can technically make a request from L1 -> L2 to impersonate Alice's wallet (0xABC) and bypass theonlyDelegate
modifier on ZkSync.
Additionally, Bob could make a L1 -> L2 request by calling the ZKSync'sBridgeFacet.xcalldirectly to steal
Alice's approved funds. Since the xcall relies onmsg.sender, it will assume that the caller is Alice.
This issue is only specific to ZkSync chain due to the preservation ofmsg.senderfor L1 -> L2 calls. For the other
chains, themsg.senderis not preserved for L1 -> L2 calls and will always point to the L2's AMB forwarding the
requests.
**Recommendation:** Due to the preservation ofmsg.senderfor L1 -> L2 calls in ZkSync chain, any contracts
deployed on ZkSync chain that relies onmsg.senderfor access control should be aware of the possibility that the
same address on Ethereum and ZkSync chains might belong to two different owners.
This issue will only happen if contract-based accounts are involved. It does not affect EOA as only the owner who
has the private key of the EOA can control the EOA on any EVM chain. If Connext plans to support ZkSync, it is
recommended that only EOA can interact with ZkSync.
Otherwise, add a disclaimer/comment informing the users about the risks and asking them to verify that they have
ownership of the address in both Ethereum and ZKSync before proceeding to interact with ZkSync.
**Connext:** Update from zkSync Team: We have a different address generation schema that would not allow ad-
dress to be claimed on L2 by an adversary. Even if you deploy same address and same private key it would be
different.
**Spearbit:** Acknowledged, since ZkSync L2 is using a different address generation schema as per the ZkSync
team, this attack vector will not be possible.
