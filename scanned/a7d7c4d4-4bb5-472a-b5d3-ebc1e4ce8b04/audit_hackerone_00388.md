# [M] Corrupt RPC responses from remote daemon nodes can lead to transaction tracing

## Summary
Severity: Medium
Program: Monero
Weakness: Privacy Violation
Reporter: monero-hax123
State: resolved
Disclosed: 2018-03-16T22:10:21.957Z
Source: https://hackerone.com/reports/304770

## Details
Dear Monero security team,
    We’re writing to disclose a privacy vulnerability when using monero-cli or monero-gui with an untrusted remote node.

When using a remote node, the Monero client relies on the node to provide information from the blockchain, in particular the public keys and transaction outputs corresponding to mixins that the client chooses by global index (gidx). The client selects a handful of gidxs, and passes these in a request to the “get_outs.bin” RPC endpoint. The client is generally designed to provide *untraceability* even against the untrusted remote node, e.g. by masking which index in the request is the real one being spent. However, if the remote node provides an invalid response then the client may end up inadvertently revealing information about the real gidx being spent.

In more detail there, we've made a proof-of-concept of two forms of this attack:

#1 Retry-and-intersect attack. 
====
If the attacker remote node returns bogus data, and the user *retries the same transaction* after clicking through the error message, it most likely reveals to the remote node exactly which coin in the transaction is the real one being spent.

1. The attacker modifies monerod to return all bogus public keys in response to the first “get_outs.bin” request.

2. The client reports an error that invalid data was received, but does not disconnect from the remote node or otherwise change its behavior. The outputs remain available for use.

3. If the user dismisses the error and then tries the same transaction again, then the client samples a *new set of mixins* to request along with the real output again.

4. The remote node looks at the two requests. Most likely, there is a unique intersection between the two sets of requested gidxs, which corresponds to the real transaction output.

5. The remote node responds to the second request with correct data, so the transaction goes through.
As a proof of concept, we tested this 10 times with a monero-cli and our own modified monerod, and found that the correct output was detected in each trial. It is possible that two such requests do not have a unique intersection, but this appears to happen with low frequency.

This is an active attack, and involves showing an error message to the client. This would likely raise suspicion if occurred many times in a row. However, since the transaction goes through without error on the second request, used sparingly it may not raise suspicion.

#2 Guess-and-check attack
====
If the remote node returns bogus data for some but not all of of the requested gidxs, then by observing the client’s behavior it can tell whether the real transaction input is one of the bogus ones or not.

1. The attacker modifies monerod to return bogus public keys for all but one of the requested gidxs. There are two cases, depending on whether the real transaction input is one of the bogus ones.

2a. The real input is one of the bogus public keys.
   The client is able to identify the incorrect response. It throws an exception, and will not sign and transmit any transaction (until after making subsequent get_out.bin requests). The attacker learns that the real transaction input is not one of the bogus ones.

2b. The real input corresponds to the non-bogus response

   The wallet is unable to discover that the response is invalid, and therefore proceeds to sign and transmit the transaction to the remote node. The attacker learns that the real transaction input is the bogus one.

Since the transaction is invalid, it will not show up on the blockchain. However, the client stores the transaction in the wallet as “pending”, such that its transaction inputs will not be reused again for 24 hours.

_Trimmed to 38 lines — full report: https://hackerone.com/reports/304770_
