# [H] Ethermint vulnerable to DoS through unintended Contract Selfdestruct

## Summary
Severity: High
Chain: github.com/evmos/ethermint
Component: github.com/evmos/ethermint, github.com/evmos/evmos, github.com/crypto-org-chain/cronos, github.com/Kava-Labs/kava
CVE: CVE-2022-35936
CWE: Exposure of Resource to Wrong Sphere
Published: 2022-08-18
Source: https://github.com/advisories/GHSA-f92v-grc2-w2fg
Type: github-advisory

## Details
# Vulnerability Report

## Impact

Smart contract applications that make use of the `selfdestruct` functionality and their end-users.

## Classification

The vulnerability has been classified as `high` with a CVSS score of `8.2`. It has the potential to create a denial-of-service to all contracts that can invoke the [`selfdestruct`](https://ethereum.stackexchange.com/questions/315/why-are-selfdestructs-used-in-contract-programming#347) function to destroy a smart contract. 

## Users Impacted

Due to the successfully coordinated security vulnerability disclosure, no smart contracts were impacted through the use of this vulnerability. Smart contract states and storage values are not affected by this vulnerability. User funds and balances are safe.

## Disclosure

In Ethermint running versions before `v0.17.2`, the contract `selfdestruct` invocation permanently removes the corresponding bytecode from the internal database storage. However, due to a bug in the [`DeleteAccount`](https://github.com/evmos/ethermint/blob/c9d42d667b753147977a725e98ed116c933c76cb/x/evm/keeper/statedb.go#L199-L203) function, all contracts that used the identical bytecode (i.e shared the same `CodeHash`) will also stop working once one contract invokes `selfdestruct`, even though the other contracts did not invoke the `selfdestruct` OPCODE.

### Additional Details

The same contract bytecode can be deployed multiple times to create multiple contract instances. In the internal database, the bytecode is stored as a key-value entry `bytecode hash --> bytecode` which is shared by those contracts. Unfortunately, when one of the contracts invokes `selfdestruct`, it will remove the corresponding `bytecode hash -> bytecode` entry, and thus it disables all the contracts that share the same bytecode.

The attack scenario is as follows:

1. The malicious attacker identifies a vulnerable contract that can invoke `selfdestruct`
2. The attacker deploys a copy of the contract with identical bytecode
3. Finally, the attacker triggers the `selfdestruct` operation on their redeployed contract, actively causing a DoS on the original and vulnerable contract. All transactions will fail until a workaround is used (see below).

## Patches

*Has the problem been patched? What versions should users upgrade to?*

This vulnerability has been patched in Ethermint versions ≥[v0.18.0](https://github.com/evmos/ethermint/releases/tag/v0.18.0). The patch has state machine-breaking changes for applications using Ethermint so a coordinated upgrade procedure is required.

#### Details

The patch removes the bytecode deletion logic, i.e. contract bytecodes are never deleted from the internal database after the patch.
At the moment, Ethermint does not track how many times each bytecode is used, and thus it cannot determine if it is safe to delete a particular bytecode on `selfdestruct` invocations. This behavior is the same with go-ethereum.

_Trimmed to 38 lines — full report: https://github.com/advisories/GHSA-f92v-grc2-w2fg_
