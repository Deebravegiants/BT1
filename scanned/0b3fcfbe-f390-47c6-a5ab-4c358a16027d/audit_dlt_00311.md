# [M] EL-2026-22: Caplin remote DoS via snappy decompression unbounded allocation

## Summary
Severity: Medium
Chain: Ethereum (execution layer)
Component: Erigon
Source: https://notes.ethereum.org/11iwNSbtSYO8mp82UYesnA
Type: ef-disclosure

## Details
Short description *
1 sentence description of the bug
Erigon remote DoS
Attack scenario *
More detailed description of the attack/bug scenario and unexpected/buggy behaviour
Malformed p2p packet
Impact *
 Describe the effect this may have in a production setting
Remote DoS, possible node crash due to OOM
Components *
Point to the files, functions, and/or specific line numbers where the bug occurs
Caplin
Reproduction *
If used any sort of tools/simulations to find the bug, describe in detail how to reproduce the buggy behaviour.


The issue is similar to CL-2020-21 (Gossip MsgID with snappy alloc blowup).

Basically, what happens is that Erigon's consensus layer calls msgId() functio on each incoming p2p message, which does the following:


https://github.com/erigontech/erigon/blob/main/cl/sentinel/msg_id.go#L35

```
func (s *Sentinel) msgId(pmsg *pubsubpb.Message) string {
        topic := *pmsg.Topic
        topicLen := len(topic)
        topicLenBytes := utils.Uint64ToLE(uint64(topicLen)) // topicLen cannot be negative

        // beyond Bellatrix epoch, allow 10 Mib gossip data size
        gossipPubSubSize := s.cfg.NetworkConfig.GossipMaxSizeBellatrix

        decodedData, err := utils.DecompressSnappy(pmsg.Data)
        if err != nil || uint64(len(decodedData)) > gossipPubSubSize {
                totalLength :=
                        len(s.cfg.NetworkConfig.MessageDomainValidSnappy) +
                                len(topicLenBytes) +
                                topicLen +
```

_Trimmed to 38 lines — full report: https://notes.ethereum.org/11iwNSbtSYO8mp82UYesnA_
