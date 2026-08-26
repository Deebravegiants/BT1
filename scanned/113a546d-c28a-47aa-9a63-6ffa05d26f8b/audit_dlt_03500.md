# [M] Distribution module address can be used to halt chain breaking all functionality.

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-11-zetachain
Published: 2023-12-05
Source: https://github.com/code-423n4/2023-11-zetachain-findings/issues/176
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/app/app.go#L185-L199


# Vulnerability details

## Impact
Currently any account can send funds to the `distribution` module account breaking the crisis invariant and causing a complete consensus failure resulting in no new blocks being produced.

In Cosmos based blockchains there are whats called `module accounts`. During development extra care has to be taken to ensure that module accounts cannot receive any funds outside of the expected rules of the state machine. If they do this can cause invariants to be broken and result in a halted network. Do to this fact the `x/bank` module accepts a map of addresses that are considered blocklisted from directly receiving funds through arbitrary transactions. 

In the ZetaChain blockchain there are many module accounts that can properly accept funds without breaking the rules of the state machine.  The vulnerability is that the  `distribution`  module account can accept funds from arbitrary users, but does so in a way that breaks the state machine.  

Along with causing a total consensus failure, this bug does not allow for any new blocks to be produced which results in an inability to accept new transactions and brings the chain to a complete halt.  With regard to blockchain bugs, this is among some of the worst possible scenarios that can take place in a distribution state machine. Imagine being able to bring Ethereum to a halt by simply sending 1 wei to a certain address. 

The likelihood of this being exploited in the future is high since it's simply a transfer of tokens from one account to another.

## Proof of Concept
Cosmos Documentation related to this issue located [here](https://docs.cosmos.network/v0.46/modules/bank/02_keepers.html#common-types)

## POC
1. Run `make install`

2. Inside the `cmd/zetacored` folder run the command `go build`.  This will create the blockchains binary `zetacored` which you will use the interact with the blockchain while the node is running. 

3. Run the command `make init`.  I added the genesis account `tommy` to get the chain to start properly and the changes I made to `init.sh` which is run by the `make init` command are as follows:

```

#!/usr/bin/env bash

CHAINID="localnet_101-1"
KEYRING="test"
export DAEMON_HOME=$HOME/.zetacored
export DAEMON_NAME=zetacored

### chain init script for development purposes only ###
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-11-zetachain-findings/issues/176_
