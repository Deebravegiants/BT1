# [C] in3-server - amplified DDoS on incubed requests on proof with signature

## Summary
Severity: Critical
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description
It is possible for a client to send a request to each node of the network to request a signature with proof for every other node in the network. This can result in DDoSing the network as there are no costs for the client to request this and client can send the same request to all the nodes in the network, resulting in `n^2` requests.

#### Examples

1. Client asks each node for `in3_nodeList` to get all the signer addresses, this could also be done using `NodeRegistry` contract
2. Client asks each node for a proof with signature, e.g.:
```js
{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "eth_getTransactionByHash",
    "params": ["0xf84cfb78971ebd940d7e4375b077244e93db2c3f88443bb93c561812cfed055c"],
    "in3": {
        "chainId": "0x1",
        "verification": "proofWithSignature",
        "signatures":["0x784bfa9eb182C3a02DbeB5285e3dBa92d717E07a", ALL OTHER SIGNERS HERE]
  }
}
```
All the nodes are now sending requests to each other with signature required which is an expensive computation. This can go on for more transactions (or blocks, or other Eth_ requests) and can result in DDoS of the network.


#### Recommendation
Limit the number of signers in proof with signature requests. Also exclude self.signer from the list. This combined with the remediation of 54 can partially mitigate the attack vector.
