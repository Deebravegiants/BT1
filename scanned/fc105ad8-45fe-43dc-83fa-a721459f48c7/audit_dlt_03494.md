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
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-11-zetachain-findings/issues/402_
