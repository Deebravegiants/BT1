# [H] TSS Key Voting Hash Collision

## Summary
Severity: High
Chain: Smart contract
Component: 2023-11-zetachain
Published: 2023-11-28
Source: https://github.com/code-423n4/2023-11-zetachain-findings/issues/133
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-11-zetachain/blob/2834e3f85b2c7774e97413936018a0814c57d860/repos/node/x/crosschain/types/message_tss_voter.go#L51-L54


# Vulnerability details

## Impact
The *Observer* role is somewhat sensitive but a single observer should not be able to influence a single action to happen. There are multiple observers with parts of the TSS key that vote on events occurring on other chains. From the documentation, *"Its important to ensure that at no time is any single entity or small fraction of nodes able to sign messages on behalf of ZetaChain on external chains"*.

When an observer is added, an observer is removed or the admin simply asks, the TSS key is regenerated. The full flow of this is explained below: 

1. Start keygen is triggered. 
2. Zetaclient does the key generation process with the other observers.
3. Observers vote on the new public key via the ``CreateTSSVoter`` message to Zetachain.
4. The vote passes once 100% of Observers have voted. This updates the TSS address on Zetachain, which is then used by the Zetaclient and many other things.
5. ``MigrateTSSFunds`` message is sent to transfer funds from the old address to the new one for each chain, which is only callable by an admin group.
6. TSS address is updated on all chains manually for the ERC20Custody contract and Connectors by the admin.
7. Admin turns on inbound transactions. 
8. Everything should be functional again.

Since the TSS (threshold signature) contains all of the funds for the various blockchains (BTC, ETH, etc.) and has complete power to perform actions on the ``Connector`` contract, this process must be done securely.

The voting process for this has a catastrophic flaw: the hash used for the voting index does NOT include the public key being voted on. Since this hash is what determines if two votes are the same, the final observer can submit a public key that will be used as the voted on key. The TSS voting requires 100% of voters to agree, making it trivial to time this as the last voter. 

If an attacker exploits this, the ``MigrateTSSFunds`` message will send all of the TSS value (BTC, ETH, etc.) to an attacker controlled address. Additionally, the TSS address will be used for parsing events and for access control on the connector contract, allowing for complete compromise of these as well transactions as well. So, practically all funds are possible to steal and funds can be created out of thin air.

## Proof of Concept
The proof of concept below was added into the ``msg_tss_voter_test.go`` file under the ``x/crosschain/keeper/`` path. This creates 4 observers and the final observer submits the malicious public key. Since the vote passes and the TSS address is replaced, this will be used by the zetaclient for future operations and by the admin on the ``MigrateTSSFunds`` call.

To run, use the command ``go test -v ./x/crosschain/keeper/ -run TestTssHashCollision``.

```go
package keeper_test

import (
	"fmt"
	"testing"
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-11-zetachain-findings/issues/133_
