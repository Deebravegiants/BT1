# [?] Correct a dial race condition (#2992)

## Summary
Severity: Unknown
Chain: Ethereum
Component: sigp/lighthouse
Published: 2022-02-07
Source: https://github.com/sigp/lighthouse/commit/675c7b7e26dd0fd1cddc4bac04b99f7b9d7dd584
Type: security-commit

## Details
Correct a dial race condition (#2992)

## Issue Addressed

On a network with few nodes, it is possible that the same node can be found from a subnet discovery and a normal peer discovery at the same time.

The network behaviour loads these peers into events and processes them when it has the chance. It can happen that the same peer can enter the event queue more than once and then attempt to be dialed twice. 

This PR shifts the registration of nodes in the peerdb as being dialed before they enter the NetworkBehaviour queue, preventing multiple attempts of the same peer being entered into the queue and avoiding the race condition.
