# [M] Malicious peer can cause a sync

## Summary
Severity: Medium
Contest weight: 0.1473
Dataset id: 23057
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The system uses a vulnerable CometBFT version. An attacker can abuse this to cause a panic during blocksync.
In go.mod, the CometBFT version is pinned to v0.38.6. This version is vulnerable to GO-2024-2951. More details about the vulnerability are available here.
The vulnerability allows an attacker to DoS the network by causing panics in all nodes during blocksync.
d/main.go#L15
The vulnerability itself is in CometBFT, but the following calls in Allora call into vulnerable code:
#1: cmd/allorad/main.go:15:26: allorad.main calls cmd.Execute, which eventually calls blocksync.BlockPool.OnStart
#2: cmd/allorad/main.go:15:26: allorad.main calls cmd.Execute, which eventually calls blocksync.NewReactor
#3: cmd/allorad/main.go:15:26: allorad.main calls cmd.Execute, which eventually calls blocksync.Reactor.OnStart
#4: cmd/allorad/main.go:15:26: allorad.main calls cmd.Execute, which eventually calls blocksync.Reactor.Receive
#5: cmd/allorad/main.go:15:26: allorad.main calls cmd.Execute, which eventually calls blocksync.Reactor.SwitchToBlockSync

## Recommendation
Update CometBFT to v0.38.8.
