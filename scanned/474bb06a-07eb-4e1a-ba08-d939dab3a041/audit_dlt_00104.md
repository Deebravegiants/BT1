# [C] ASA-2025-004: Non-deterministic JSON Unmarshalling of IBC Acknowledgement can result in a chain halt

## Summary
Severity: Critical
Chain: Cosmos
Component: cosmos/ibc-go
CWE: Deserialization of Untrusted Data
Published: 2025-02-27
Source: https://github.com/cosmos/ibc-go/security/advisories/GHSA-jg6f-48ff-5xrw
Type: github-advisory

## Details
Name: ASA-2025-004: Non-deterministic JSON Unmarshalling of IBC Acknowledgement can result in a chain halt
Component: IBC-Go
Criticality: Critical (Considerable Impact; Almost Certain Likelihood per [ACMv1.2](https://github.com/interchainio/security/blob/main/resources/CLASSIFICATION_MATRIX.md))
Affected versions: IBC-Go >= v7; Earlier IBC-Go versions may also be affected.
Affected users: Validators, Full nodes, IBC Middleware authors

### Description

An issue was discovered in IBC-Go's deserialization of acknowledgements that results in non-deterministic behavior which can halt a chain. Any user that can open an IBC channel can introduce this state to the chain

### Patches

The new IBC-Go releases below address this issue:

* [v7.9.2](https://github.com/cosmos/ibc-go/releases/tag/v7.9.2)
* [v8.6.1](https://github.com/cosmos/ibc-go/releases/tag/v8.6.1)

### Workarounds

To prevent this state from being introduced to a chain, it is possible to permission Channel Opening as a workaround.

### Notes on Re-Release

#### Is this state breaking? Probably not but it depends on your transfer middlewares

This patch is not state breaking unless you depend on transfer middlewares that deserialize and serialize acknowledgement packets before passing them to the transfer handler.  As far as we can tell, these middlewares are rare. For example, packet-forward-middleware and ibc-hooks, do not serialize ack packets in this way and therefore aren't broken by this patch. So if these are the only transfer middlewares you depend on, you can safely apply this patch in a rolling manner (and we've already cut new versions of these for you).

#### What to do if you do depend on ack-serializing middleware

In the unlikely case that you depend on middlewares that serialize ack packets and you do not update them when you apply this patch, all transfers that are handled by the middleware will fail (or experience other unexpected behavior) if the serialization approach differs from the transfer app's. If you have such dependencies and do not update them, validators who apply the patch in a rolling manner will halt when they upgrade, and transfers processed by the middleware will just fail once everyone has upgraded.

To update these middlewares and avoid failing transfers or a chain halt, you will simply need to change the serialization approach in the middleware to use ibc-go's codec: `transfertypes.ModuleCdc.[Must]MarshalJSON`, rather than whatever you're doing today.  For example:

```
import transfertypes "github.com/cosmos/ibc-go/v10/modules/apps/transfer/types"
transfertypes.ModuleCdc.[Must]MarshalJSON
func MarshalAsIBCDoes(ack channeltypes.Acknowledgement) ([]byte, error) {
	return transfertypes.ModuleCdc.MarshalJSON(&ack)
}
```
When you do make a change to the serialization approach, this will make the patch state breaking and you will need a coordinated upgrade. So for absolute clarity: chains with these ack-serializing middlewares must do coordinated upgrades

#### Why we retracted the earlier patch in favor of this approach
We retracted the releases of ibc-go we cut earlier today because these broke all transfer middlewares that deserialized then re-serialized receive packets differently than the transfer app. It turned out that this was a common pattern (unlike serializing/deserializing ack packets), so widely used middlewares, including packet-forward-middleware, broke unexpectedly.

In the new set of patches, we removed this constraint on how middlewares serialize receive packets, preventing this breakage. Only the serialization requirement on acknowledgement packets remains. This is convenient because this is the only constraint we had to add to fix the vulnerability, and middlewares that deserialize and serialize ack packets are much less common than ones that do so for receive packets. The constraint on receive packets was added for defense in depth.

#### Testing we have done to gain more confidence in this release
* In addition to testing ibc-go, we also did the following:
* Tested pfm v7 and v8 after bumping dependencies
* Tested ibc-hooks v7 and v8 after bumping dependencies
* Ran a patched node on mainnet on the cosmos hub and triggered failing and successful transactions that used PFM
* Ran a patched node on osmosis and triggered failing and successful transactions that used ibc-hooks
This is a more thorough process than before, so we have higher confidence.

### Timeline

* February 18, 2025, 4:54am PST: Issue reported to the Cosmos Bug Bounty program
* February 18, 2025, 6:56am PST: Issue triaged by Amulet on-call, and distributed to Core team
* February 18, 2025, 8:15am PST: Core team completes validation of issue
* February 25, 2025, 8:00am PST / 17:00 CET: Pre-notification delivered
* February 27, 2025, 8:00am PST / 17:00 CET: Patch made available
* February 27, 2025, 1:00pm PST: Patch re-release made available

This issue was reported to the Cosmos Bug Bounty Program by swelf19 on HackerOne on February 18, 2025. If you believe you have found a bug in the Interchain Stack or would like to contribute to the program by reporting a bug, please see https://hackerone.com/cosmos.

If you have questions about Interchain security efforts, please reach out to our official communication channel at [security@interchain.io](mailto:security@interchain.io). For more information about the Interchain Foundation’s engagement with Amulet, and to sign up for security notification emails, please see https://github.com/interchainio/security.  

A Github Security Advisory for this issue is available in the IBC-Go [repository](https://github.com/cosmos/ibc-go/security/advisories/GHSA-jg6f-48ff-5xrw).
