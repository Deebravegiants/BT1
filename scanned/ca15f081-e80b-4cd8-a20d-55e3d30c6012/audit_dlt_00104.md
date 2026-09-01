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
```

_Trimmed to 38 lines — full report: https://github.com/cosmos/ibc-go/security/advisories/GHSA-jg6f-48ff-5xrw_
