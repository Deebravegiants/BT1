# [H] Using unconfirmed UTXOs as inputs for transactions is vulnerable to griefing attacks

## Summary
Severity: High
Chain: Smart contract
Component: 2023-11-zetachain
Published: 2023-12-17
Source: https://github.com/code-423n4/2023-11-zetachain-findings/issues/402
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/bitcoin_client.go#L737


# Vulnerability details

## Impact

BTC transactions originating from the TSS address can be griefed by an attacker, preventing the TSS address from sending BTC transactions.

## Proof of Concept

The Bitcoin client retrieves all UTXO's for the TSS address with the [`FetchUTXOS`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/bitcoin_client.go#L711-L759) function. Subsequently, the UTXO's are [used as inputs for outgoing cctx's](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/btc_signer.go#L90) to cover the expenses of the transaction.

Concretely, the UTXOs are queried from the RPC by calling the `ListUnspentMinMaxAddresses` function in line [`737`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/bitcoin_client.go#L737). However, the first argument, the minimum number of confirmations, is set to 0.

```go
File: bitcoin_client.go
711: func (ob *BitcoinChainClient) FetchUTXOS() error {
...  	// [...]
720:
721: 	// get the current block height.
722: 	bh, err := ob.rpcClient.GetBlockCount()
723: 	if err != nil {
724: 		return fmt.Errorf("btc: error getting block height : %v", err)
725: 	}
726: 	maxConfirmations := int(bh)
727:
728: 	// List unspent.
729: 	tssAddr := ob.Tss.BTCAddress()
730: 	address, err := btcutil.DecodeAddress(tssAddr, config.BitconNetParams)
731: 	if err != nil {
732: 		return fmt.Errorf("btc: error decoding wallet address (%s) : %s", tssAddr, err.Error())
733: 	}
734: 	addresses := []btcutil.Address{address}
735:
736: 	// fetching all TSS utxos takes 160ms
737: ❌	utxos, err := ob.rpcClient.ListUnspentMinMaxAddresses(0, maxConfirmations, addresses)
...  	// [...]
759: }
```

As a result, the UTXOs returned by the RPC call include unconfirmed UTXOs, i.e., transaction outputs that are not yet confirmed by subsequent blocks.

Consequently, an attacker can craft a BTC transaction to the TSS address, with a low fee, and broadcast it to the network (the transaction outputs must match the range of UTXOs that will be used by the TSS address for the next transaction). While the transaction and its outputs are sitting unconfirmed in the mempool, the observer Bitcoin clients will retrieve these unconfirmed outputs as UTXOs.

The unconfirmed UTXOs are then used as inputs for outgoing TSS BTC transactions, which will also remain unconfirmed as long as the original transaction (from the attacker) remains unconfirmed. This can cause a halt in the outgoing BTC transactions from the TSS address.

Moreover, the attacker can replace the original transaction via the [Replace-by-fee (RBF) policy](https://bitcoinops.org/en/topics/replace-by-fee/), and change the recipient address to an address other than the TSS address. This will render the UTXOs used as inputs for the TSS's outgoing transaction invalid, causing the outgoing transaction to fail.

Comparing ZetaChain's UTXO retrieval mechanism with Thorchain's implementation, the latter treats unconfirmed UTXOs separately by checking if the UTXO was self-sent or sent from the Asgard address:

[bifrost/pkg/chainclients/bitcoin/client.go#L274-279](https://gitlab.com/thorchain/thornode/-/blob/develop/bifrost/pkg/chainclients/bitcoin/client.go#L274-279)

```go
if item.Confirmations == 0 {
  // pending tx in mempool, only count sends to self or from asgard
  if !c.isSelfTransaction(item.TxID) && !c.isAsgardAddress(item.Address) {
    continue
  }
}
```

[`Client.isSelfTransaction`](https://gitlab.com/thorchain/thornode/-/blob/4bf0118790ff3440c30ea64712af72f480b89cac/bifrost/pkg/chainclients/bitcoin/signer.go#L152-L170)

```go
// isSelfTransaction check the block meta to see whether the transactions is broadcast by ourselves
// if the transaction is broadcast by ourselves, then we should be able to spend the UTXO even it is still in mempool
// as such we could daisy chain the outbound transaction
func (c *Client) isSelfTransaction(txID string) bool {
	bms, err := c.temporalStorage.GetBlockMetas()
	if err != nil {
		c.logger.Err(err).Msg("fail to get block metas")
		return false
	}
	for _, item := range bms {
		for _, tx := range item.SelfTransactions {
			if strings.EqualFold(tx, txID) {
				c.logger.Debug().Msgf("%s is self transaction", txID)
				return true
			}
		}
	}
	return false
}
```

## Tools Used

Manual review

## Recommended mitigation steps

Consider only using unconfirmed UTXOs as inputs for outgoing transactions if the UTXOs were sent from the TSS address, similar to Thorchain's implementation.



## Assessed type

Invalid Validation
