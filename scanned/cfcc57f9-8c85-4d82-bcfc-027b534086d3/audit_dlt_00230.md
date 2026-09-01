# [M] CL-2021-03: Mplex unlimited open streams + bad Prysm rate limit + stall on SSZ decode

## Summary
Severity: Medium
Chain: Ethereum (consensus layer)
Component: Prysm
Published: 2021-12-01
Source: https://gist.github.com/protolambda/c45a4d9167fc4b20f2f76c749eeb7105
Type: ef-disclosure

## Details
# Prysm DoS

Found by @protolambda, 12 Feb.

Results: 10+ GB instantenous memory jump and brief max-CPU usage. (I didn't try more aggresive dos parameters, it doesn't seem limited here)

Affected version:
```
commit 473172ca8b6a1adb3a825c74b5318df5c3fdb049 develop
Date:   Fri Feb 12 13:06:58 2021 -0600
```
I.e. latest Prysm, and all previous versions are likely affected.

How:
- Go Mplex does not limit the amount of open channels
- Go Mplex multiplexes the (secured) connection into streams
- Two frames per payload: create a unique nameless channel, and fill the channel with pro-active multiselect negotiation and the actual payload.
- Multiselect just says "oh this looks like an Eth2 status RPC stream, carry on"
- Swarm (internals of libp2p host) just accept the stream, wrap it with above negotiation, and fire a go routine for every stream
- **Prysm does not rate-limit before decoding**
  - Entry point hits decoding before the type-specific rate-limiting: https://github.com/prysmaticlabs/prysm/blob/0716519be90ca91e2bc79891def2ac28204b4e38/beacon-chain/sync/rpc.go#L64
- the 2nd mplex frame per payload has something special to be decoded (after the protocol negotiation): a varint that declares the length of a 1 MB SSZ blob.
  - The 1 MB is pre-allocated for further decoding, for each of those frames. The stream is never continued, no more frames, Prysm won't get to decode anything.
    - Prysm decoding code: https://github.com/prysmaticlabs/prysm/blob/0716519be90ca91e2bc79891def2ac28204b4e38/beacon-chain/p2p/encoder/ssz.go#L138
  - Prysm does not have strict request size limits per type. Other clients limit requests to sensible sizes within Eth2 type bounds (a few hundred bytes), and thus less prone to DoS (untested though).
- Attackers puts 100.000 of these tiny payloads (< 100 bytes each, thus < 10 MB total) and sends it all at once to the connected Prysm node.
- The attack can be repeated at low cost too.

Demo screenshot:
![](https://storage.googleapis.com/ethereum-hackmd/upload_3fe3c39f17ab162638a5bbb2a2d70252.png)

Hacky code to demonstrate attack:

*Note, forked gp-mplex, libp2p-go-mplex, and libp2p-swarm to gain access to private API methods, and had to use older versions since Rumor is not updated to latest libp2p yet.
With that I was able to hijack mplex loop on live connection, and get the rumor node to attack a local Prysm node.*

New in rumor: `dos.go` for DoS command
```go
```

_Trimmed to 38 lines — full report: https://gist.github.com/protolambda/c45a4d9167fc4b20f2f76c749eeb7105_
