# [C] Attacker can add arbitrary data to the blockchain without paying gas

## Summary
Severity: Critical (CVSS 9.3)
Program: Rootstock Labs
Weakness: Deserialization of Untrusted Data
Reporter: ahook
State: resolved
Disclosed: 2019-09-18T13:18:55.944Z
Source: https://hackerone.com/reports/396954

## Details
**Summary:**
Due to a missing sanity check in Transaction::rlpParse, an attacker can append arbitrary RLP-encoded data to the end of an otherwise valid transaction, and that data will not only pass through validation, but also be propagated throug the network and mined into a block. Since the block parser uses the same code for decoding transactions (as it should), the block will also be conidered valid.

**Description:**
The issue stems from the Transaction::rlpParse function:
https://github.com/rsksmart/rskj/blob/master/rskj-core/src/main/java/org/ethereum/core/Transaction.java#L242

Once all the relevant data is pulled from the decoded RLP, there are no checks to ensure that we've reached the end of the data.

Since the transaction is constructed using the raw encoded bytes, any future calls to getEncoded() will return the entire byte array, including the bad data at the end. Signature verification of the valid transaction will still pass because it uses getRawEncoded() to compute the signature, which ignores the extra data.

## Steps To Reproduce:
On a remote server I start up a regtest node from a clean codebase. This will begin mining as a single-node network:
```
remote:~/rskj$ java -Dblockchain.config.name=regtest -cp rskj-core/build/libs/rskj-core-0.5.0-SNAPSHOT-all.jar co.rsk.Start
```

On my local machine, I start another regtest node but I modify the config to a) talk to my remote node, and b) not mine. I don't mine on this node because I will be using it to manufacture beefy transactions and I want to make sure that other, clean nodes will accept/mine these transactions.

In addition to the config changes, I have also modified the eth_sendTransaction code to add extra rlp-encoded bytes to the end of the transaction. In order to easily see the data in a hex blob, I'm just setting it to a repeated 0xbeef string. I've also hacked the getBlockByHash function to return the full encoded hex block in the extraData field, as a quick way to query and see the raw block data.

```
local:~/rskj$ # Start the attacker's node:
local:~/rskj$ java -Dblockchain.config.name=regtest -cp rskj-core/build/libs/rskj-core-0.5.0-SNAPSHOT-all.jar co.rsk.Start
local:~/rskj$
local:~/rskj$ # Create a new account:
local:~/rskj$ curl -s -X POST -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","method":"personal_newAccount", "params": ["beef"], "id":666}' http://127.0.0.1:4444/
{"jsonrpc":"2.0","id":666,"result":"0x0e016bdab929a365c7419ba51d0902cbde6035c2"}
local:~/rskj$
local:~/rskj$ # Send a transaction:
local:~/rskj$ curl -s -X POST -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","method":"eth_sendTransaction", "params": [{"from": "0xCd2a3d9f938e13Cd947eC05ABC7fe734df8DD826", "to":"0x0e016bdab929a365c7419ba51d0902cbde6035c2", "gas":"0x76c0", "gasPrice": "0x9184e72a000", "value":"0x9184e72a"}], "id":666}' http://127.0.0.1:4444/
{"jsonrpc":"2.0","id":666,"result":"0x26ef60114e110258b1f6427042345c401068c9c666e0782f3d597c73ef1eb301"}
local:~/rskj$
local:~/rskj$ # Wait for the transaction to propagate to the remote server and be mined
local:~/rskj$ # Then check the receipt to see that it made it into the block:
local:~/rskj$ $ curl -s -X POST -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","method":"eth_getTransactionReceipt", "params": ["0x26ef60114e110258b1f6427042345c401068c9c666e0782f3d597c73ef1eb301"], "id":666}' http://127.0.0.1:4444/
{"jsonrpc":"2.0","id":666,"result":{"transactionHash":"0x26ef60114e110258b1f6427042345c401068c9c666e0782f3d597c73ef1eb301","transactionIndex":"0x0","blockHash":"0x2d1333a31807d2ce3f058bf8ffe10a343b6d8fc59b7a918c3004fd1e46880747","blockNumber":"0x681","cumulativeGasUsed":"0x5208","gasUsed":"0x5208","contractAddress":null,"logs":[],"from":"0xcd2a3d9f938e13cd947ec05abc7fe734df8dd826","to":"0x0e016bdab929a365c7419ba51d0902cbde6035c2","root":"0x01","status":"0x01"}}
local:~/rskj$
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/396954_
