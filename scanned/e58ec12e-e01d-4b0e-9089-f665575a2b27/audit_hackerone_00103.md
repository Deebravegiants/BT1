# [H] DOS validator nodes of blockchain to block external connections

## Summary
Severity: High (CVSS 7.5)
Program: Linux Foundation Decentralized Trust
Weakness: Uncontrolled Resource Consumption
Reporter: cre8
State: resolved
Disclosed: 2022-09-13T07:56:43.496Z
CVE: CVE-2022-31006
Source: https://hackerone.com/reports/1695472

## Details
Attack was documented in the in the github repo: https://github.com/hyperledger/indy-node/security/advisories/GHSA-x996-7qh9-7ff7

# Attack:
The attacker sends 500 read requests to each node and opens a new one when
holding 500 parallel connections. Every user is able to send read requests
since it's a public readable registry so setting up an allowlist like it's
done with the nodes' port for the consensus does not work here. To increase
the efficiency:

the custom read request is increased with more bytes (random header or
json values)
the bandwidth of the sender machine is limited
Requirements on the attacker side:
Indy-VDR: comment out the timeouts. Using another tool to send the requests
could be even more efficient
VM: attack can be performed from one or multiple VMs limited connection: using
TC to limit the bandwidth (value depends on the amount of connections)
Sample Implementation
We set up a VON-Network and added the firewall rules. The VM had 32 CPUs
and 64 GB RAM

# Result:
there is no damage to the blockchain, only an unreachable network as long
as the attack is going on .
Other clients are not able to send read or write requests to the nodes. In
the "best case" their requests will go through but with a response time of
multiple seconds, see:
Not available [image: image.png]

Not available [image: image.png]

# Counteractions:
blacklisting actors: It does not matter what is in the body since the
firewall rule acts in front of indy that is processing the information. To
avoid big requests the firewall could set a limit of the request size, but
this could also block valid requests.
Scaling via the observer-pattern: Right now the amount of nodes is
limited so blocking 25*500 connections is very easy. When adding nodes in

_Trimmed to 38 lines — full report: https://hackerone.com/reports/1695472_
