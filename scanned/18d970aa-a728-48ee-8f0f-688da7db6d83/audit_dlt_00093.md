# [M] ASA-2023-001: Cosmovisor

## Summary
Severity: Medium
Chain: Cosmos
Component: cosmos/cosmos-sdk
Published: 2023-09-06
Source: https://github.com/cosmos/cosmos-sdk/security/advisories/GHSA-23px-mw2p-46qm
Type: github-advisory

## Details
**Component**: Cosmovisor
**Criticality**: Medium
**Affected Versions**: Cosmovisor < v1.0.0 (distributed with Cosmos-SDK < 0.46)
**Affected Users**: Validators and Node operators utilizing unsupported versions of Cosmovisor
**Impact**: DOS, potential RCE on node depending on configuration


An issue has been identified on unsupported versions of Cosmovisor which may result in a Denial of Service or Remote Code Execution path depending on configuration for a node or validator using the vulnerable version to manage their node. 

If a validator is utilizing an affected version of Cosmovisor with `DAEMON_ALLOW_DOWNLOAD_BINARIES` set to true, a non-default configuration, it may be possible for an attacker to trigger a Remote Code Execution path as well on the host. In this configuration it is recommended to immediately stop use of the `DAEMON_ALLOW_DOWNLOAD_BINARIES` feature, and then proceed with an upgrade of Cosmovisor.

It is recommended that all validators utilizing unsupported versions of Cosmovisor to upgrade to the latest supported versions immediately.  If you are utilizing a forked version of Cosmos-SDK, it is recommended to stop use of Cosmovisor until it is possible to update to a supported version of Cosmovisor, whether through your project’s fork, or directly compiled from the Cosmos-SDK. At the time of this advisory, the latest version of Cosmovisor is v1.5.0. 

Additionally, the Amulet team recommends that developers building chains powered by Cosmos-SDK share this advisory with validators and node operators to ensure this information is available to all impacted parties within their ecosystems.

For more information about Cosmovisor, see https://docs.cosmos.network/main/tooling/cosmovisor

This issue was discovered by [Maxwell Dulin](https://maxwelldulin.com) and Nathan Kirkland, who reported it to the Cosmos Bug Bounty Program.  If you believe you have found a bug in the Interchain Stack or would like to contribute to the program by reporting a bug, please see [https://hackerone.com/cosmos](https://hackerone.com/cosmos).

## How to tell if I am affected?

Running the following command will output whether your cosmovisor version is vulnerable to this issue or not.  

Vulnerable to this issue: 

```
strings ./cosmovisor | grep -q "NEEDED at" && echo "vulnerable" || echo "NOT vulnerable"

vulnerable
```


NOT vulnerable to this issue:

```
strings ./cosmovisor_new | grep -q "NEEDED at" && echo "vulnerable" || echo "NOT vulnerable"

NOT vulnerable
```

_Trimmed to 38 lines — full report: https://github.com/cosmos/cosmos-sdk/security/advisories/GHSA-23px-mw2p-46qm_
