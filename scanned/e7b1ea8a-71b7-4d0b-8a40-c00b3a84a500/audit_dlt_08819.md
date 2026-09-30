# [?] fix(protocol): reject SGX instance ids that overflow the uint32 proof field (#21892)

## Summary
Severity: Unknown
Chain: Taiko
Component: taikoxyz/taiko-mono
Published: 2026-07-02
Source: https://github.com/taikoxyz/taiko-mono/commit/ac7a154e3ed74e04375949e2bf96f430d0ffa100
Type: security-commit

## Details
fix(protocol): reject SGX instance ids that overflow the uint32 proof field (#21892)

Co-authored-by: Claude <noreply@anthropic.com>

## Patch
### packages/protocol/contracts/layer1/verifiers/SgxVerifier.sol
```diff
@@ -170,6 +170,7 @@ abstract contract SgxVerifier is IProofVerifier, Ownable2Step, ReentrancyGuard {
     error SGX_INVALID_ATTESTATION();
     error SGX_INVALID_INSTANCE();
     error SGX_INVALID_PROOF();
+    error SGX_INSTANCE_ID_OVERFLOW();
     error SGX_INVALID_CHAIN_ID();
     error SGX_NOT_REGISTRAR();
 
@@ -492,6 +493,12 @@ abstract contract SgxVerifier is IProofVerifier, Ownable2Step, ReentrancyGuard {
 
             require(_instances[i] != address(0), SGX_INVALID_INSTANCE());
 
+            // `verifyProof` references an instance by a uint32 id decoded from the proof, while ids
+            // are assigned from the uint256 `nextInstanceId`. Reject any id that would not survive
+            // that truncation, so a registered instance is always reachable from a proof (a
+            // reachable-instance invariant made explicit rather than left to a silent wrap).
+            require(nextInstanceId <= type(uint32).max, SGX_INSTANCE_ID_OVERFLOW());
+
             instances[nextInstanceId] =
                 Instance(_instances[i], validSince, _policyVersion, _mrEnclave, _mrSigner);
             ids[i] = nextInstanceId;
```

### packages/protocol/gas-reports/layer1-contracts.txt
```diff
@@ -100,71 +100,72 @@ InboxWhitelistProverTest:test_prove_RevertWhen_CallerIsNotWhitelistedProverAndPr
 InboxWhitelistProverTest:test_prove_RevertWhen_NonWhitelistedProverAfterPermissionlessProvingDelay() (gas: 152333)
 InboxWhitelistProverTest:test_prove_skipsBondInstruction_whenCallerIsWhitelistedProver() (gas: 228019)
 InboxWhitelistProverTest:test_prove_succeedsWhen_CallerIsWhitelistedProver() (gas: 216979)
-InsecureSgxVerifierTest:test_addInstances_RecordsNoMrEnclave() (gas: 89310)
-InsecureSgxVerifierTest:test_addInstances_RevertWhen_DuplicateAddress() (gas: 91142)
-InsecureSgxVerifierTest:test_addInstances_RevertWhen_NotOwner() (gas: 13658)
-InsecureSgxVerifierTest:test_addInstances_RevertWhen_ZeroAddress() (gas: 36422)
-InsecureSgxVerifierTest:test_addInstances_succeeds() (gas: 143691)
-InsecureSgxVerifierTest:test_constructor_RevertWhen_ChainIdZero() (gas: 86108)
+InsecureSgxVerifierTest:test_addInstances_RecordsNoMrEnclave() (gas: 89562)
+InsecureSgxVerifierTest:test_addInstances_RevertWhen_DuplicateAddress() (gas: 91498)
+InsecureSgxVerifierTest:test_addInstances_RevertWhen_InstanceIdOverflows() (gas: 223976)
+InsecureSgxVerifierTest:test_addInstances_RevertWhen_NotOwner() (gas: 13752)
+InsecureSgxVerifierTest:test_addInstances_RevertWhen_ZeroAddress() (gas: 36516)
+InsecureSgxVerifierTest:test_addInstances_succeeds() (gas: 144033)
+InsecureSgxVerifierTest:test_constructor_RevertWhen_ChainIdZero() (gas: 86138)
 InsecureSgxVerifierTest:test_constructor_enablesLocalReportCheckByDefault() (gas: 10520)
 InsecureSgxVerifierTest:test_deleteInstances_RevertWhen_InvalidInstance() (gas: 13619)
-InsecureSgxVerifierTest:test_deleteInstances_RevertWhen_NotOwner() (gas: 11655)
-InsecureSgxVerifierTest:test_deleteInstances_succeeds() (gas: 74884)
-InsecureSgxVerifierTest:test_isTcbStatusAccepted_LenientPolicy() (gas: 18588)
+InsecureSgxVerifierTest:test_deleteInstances_RevertWhen_NotOwner() (gas: 11633)
+InsecureSgxVerifierTest:test_deleteInstances_succeeds() (gas: 75136)
+InsecureSgxVerifierTest:test_isTcbStatusAccepted_LenientPolicy() (gas: 18676)
 InsecureSgxVerifierTest:test_isTcbStatusAccepted_LenientPolicyIsExact() (gas: 433469)
-InsecureSgxVerifierTest:test_registerInstance_AcceptsOutOfDateConfigTcb() (gas: 190205)
-InsecureSgxVerifierTest:test_registerInstance_AcceptsOutOfDateTcb() (gas: 190242)
-InsecureSgxVerifierTest:test_registerInstance_AcceptsProductionAttributesWithoutPin() (gas: 188662)
-InsecureSgxVerifierTest:test_registerInstance_AllowsDebugBitOutsideFlagsByte() (gas: 188701)
-InsecureSgxVerifierTest:test_registerInstance_AllowsRegistrarWhenSet() (gas: 1698784)
-InsecureSgxVerifierTest:test_registerInstance_RecordsMrEnclave() (gas: 190897)
+InsecureSgxVerifierTest:test_registerInstance_AcceptsOutOfDateConfigTcb() (gas: 190331)
+InsecureSgxVerifierTest:test_registerInstance_AcceptsOutOfDateTcb() (gas: 190346)
+InsecureSgxVerifierTest:test_registerInstance_AcceptsProductionAttributesWithoutPin() (gas: 188788)
+InsecureSgxVerifierTest:test_registerInstance_AllowsDebugBitOutsideFlagsByte() (gas: 188827)
+InsecureSgxVerifierTest:test_registerInstance_AllowsRegistrarWhenSet() (gas: 1706732)
+InsecureSgxVerifierTest:test_registerInstance_RecordsMrEnclave() (gas: 191013)
 InsecureSgxVerifierTest:test_registerInstance_RevertWhen_AllowlistOnAndMrEnclaveUntrusted() (gas: 53034)
-InsecureSgxVerifierTest:test_registerInstance_RevertWhen_AllowlistOnAndMrSignerUntrusted() (gas: 53213)
-InsecureSgxVerifierTest:test_registerInstance_RevertWhen_CallerNotRegistrar() (gas: 1523332)
+InsecureSgxVerifierTest:test_registerInstance_RevertWhen_AllowlistOnAndMrSignerUntrusted() (gas: 53191)
+InsecureSgxVerifierTest:test_registerInstance_RevertWhen_CallerNotRegistrar() (gas: 1531176)
 InsecureSgxVerifierTest:test_registerInstance_RevertWhen_DebugEnclave() (gas: 20594)
-InsecureSgxVerifierTest:test_registerInstance_RevertWhen_DuplicateInstance() (gas: 199131)
-InsecureSgxVerifierTest:test_registerInstance_RevertWhen_InstanceZeroAddress() (gas: 99522)
+InsecureSgxVerifierTest:test_registerInstance_RevertWhen_DuplicateInstance() (gas: 199235)
+InsecureSgxVerifierTest:test_registerInstance_RevertWhen_InstanceZeroAddress() (gas: 99500)
 InsecureSgxVerifierTest:test_registerInstance_RevertWhen_LaunchKeyEnabled() (gas: 21987)
-InsecureSgxVerifierTest:test_registerInstance_RevertWhen_NoAttestationEntrypoint() (gas: 1522887)
+InsecureSgxVerifierTest:test_registerInstance_RevertWhen_NoAttestationEntrypoint() (gas: 1530798)
 InsecureSgxVerifierTest:test_registerInstance_RevertWhen_NotVerified() (gas: 18365)
 InsecureSgxVerifierTest:test_registerInstance_RevertWhen_OutputTooShort() (gas: 18451)
 InsecureSgxVerifierTest:test_registerInstance_RevertWhen_ProvisionKeyEnabled() (gas: 21963)
 InsecureSgxVerifierTest:test_registerInstance_RevertWhen_RawQuoteTooShort() (gas: 16333)
 InsecureSgxVerifierTest:test_registerInstance_RevertWhen_TcbConfigNeeded() (gas: 19777)
-InsecureSgxVerifierTest:test_registerInstance_RevertWhen_TcbConfigNeeded() (gas: 19894)
+InsecureSgxVerifierTest:test_registerInstance_RevertWhen_TcbConfigNeeded() (gas: 19872)
 InsecureSgxVerifierTest:test_registerInstance_RevertWhen_TcbRevoked() (gas: 19754)
-InsecureSgxVerifierTest:test_registerInstance_RevertWhen_TcbRevoked() (gas: 19916)
+InsecureSgxVerifierTest:test_registerInstance_RevertWhen_TcbRevoked() (gas: 19894)
 InsecureSgxVerifierTest:test_registerInstance_RevertWhen_TcbUnrecognized() (gas: 19776)
-InsecureSgxVerifierTest:test_registerInstance_RevertWhen_TcbUnrecognized() (gas: 19850)
+InsecureSgxVerifierTest:test_registerInstance_RevertWhen_TcbUnrecognized() (gas: 19828)
 InsecureSgxVerifierTest:test_registerInstance_RevertWhen_VerifiedBodyMismatch() (gas: 20600)
-InsecureSgxVerifierTest:test_registerInstance_RevertWhen_WrongBodyType() (gas: 19611)
-InsecureSgxVerifierTest:test_registerInstance_RevertWhen_WrongQuoteVersion() (gas: 19437)
-InsecureSgxVerifierTest:test_registerInstance_WithAllowlist_succeeds() (gas: 189730)
-InsecureSgxVerifierTest:test_registerInstance_acceptsAllAllowedTcbStatuses() (gas: 400865)
-InsecureSgxVerifierTest:test_registerInstance_acceptsLenientTcbStatuses() (gas: 355594)
-InsecureSgxVerifierTest:test_registerInstance_acceptsTcbConfigAndSwHardeningNeeded() (gas: 144363)
-InsecureSgxVerifierTest:test_registerInstance_acceptsTcbOutOfDate() (gas: 144424)
-InsecureSgxVerifierTest:test_registerInstance_acceptsTcbOutOfDateConfigNeeded() (gas: 144455)
-InsecureSgxVerifierTest:test_registerInstance_doesNotForwardValue() (gas: 190866)
-InsecureSgxVerifierTest:test_registerInstance_succeeds() (gas: 196806)
+InsecureSgxVerifierTest:test_registerInstance_RevertWhen_WrongBodyType() (gas: 19589)
+InsecureSgxVerifierTest:test_registerInstance_RevertWhen_WrongQuoteVersion() (gas: 19415)
+InsecureSgxVerifierTest:test_registerInstance_WithAllowlist_succeeds() (gas: 189856)
+InsecureSgxVerifierTest:test_registerInstance_acceptsAllAllowedTcbStatuses() (gas: 401243)
+InsecureSgxVerifierTest:test_registerInstance_acceptsLenientTcbStatuses() (gas: 355972)
+InsecureSgxVerifierTest:test_registerInstance_acceptsTcbConfigAndSwHardeningNeeded() (gas: 144489)
+InsecureSgxVerifierTest:test_registerInstance_acceptsTcbOutOfDate() (gas: 144550)
+InsecureSgxVerifierTest:test_registerInstance_acceptsTcbOutOfDateConfigNeeded() (gas: 144581)
+InsecureSgxVerifierTest:test_registerInstance_doesNotForwardValue() (gas: 190970)
+InsecureSgxVerifierTest:test_registerInstance_succeeds() (gas: 196946)
 InsecureSgxVerifierTest:test_setMrEnclave_RevertWhen_NotOwner() (gas: 11145)
 InsecureSgxVerifierTest:test_setMrEnclave_setsAndEmits() (gas: 37207)
-InsecureSgxVerifierTest:test_setMrSigner_RevertWhen_NotOwner() (gas: 11132)
-InsecureSgxVerifierTest:test_setMrSigner_setsAndEmits() (gas: 37262)
-InsecureSgxVerifierTest:test_tcbStatusEnum_matchesExpectedValues() (gas: 6215)
+InsecureSgxVerifierTest:test_setMrSigner_RevertWhen_NotOwner() (gas: 11110)
+InsecureSgxVerifierTest:test_setMrSigner_setsAndEmits() (gas: 37240)
+InsecureSgxVerifierTest:test_tcbStatusEnum_matchesExpectedValues() (gas: 6193)
 InsecureSgxVerifierTest:test_toggleLocalReportCheck_RevertWhen_NotOwner() (gas: 11002)
-InsecureSgxVerifierTest:test_toggleLocalReportCheck_togglesAndEmits() (gas: 20930)
-InsecureSgxVerifierTest:test_verifyProof_AllowlistDisabledSkipsReCheck() (gas: 164424)
-InsecureSgxVerifierTest:test_verifyProof_OwnerAddedInstanceIgnoresAllowlistChanges() (gas: 107671)
-InsecureSgxVerifierTest:test_verifyProof_RevertWhen_AggregatedHashZero() (gas: 91936)
-InsecureSgxVerifierTest:test_verifyProof_RevertWhen_BadSignature() (gas: 96206)
-InsecureSgxVerifierTest:test_verifyProof_RevertWhen_Expired() (gas: 93314)
-InsecureSgxVerifierTest:test_verifyProof_RevertWhen_InstanceMismatch() (gas: 91593)
-InsecureSgxVerifierTest:test_verifyProof_RevertWhen_InstanceZero() (gas: 10021)
-InsecureSgxVerifierTest:test_verifyProof_RevertWhen_MrEnclaveUntrustedAfterRegistration() (gas: 184088)
-InsecureSgxVerifierTest:test_verifyProof_RevertWhen_MrSignerUntrustedAfterRegistration() (gas: 184376)
+InsecureSgxVerifierTest:test_toggleLocalReportCheck_togglesAndEmits() (gas: 21018)
+InsecureSgxVerifierTest:test_verifyProof_AllowlistDisabledSkipsReCheck() (gas: 164535)
+InsecureSgxVerifierTest:test_verifyProof_OwnerAddedInstanceIgnoresAllowlistChanges() (gas: 107923)
+InsecureSgxVerifierTest:test_verifyProof_RevertWhen_AggregatedHashZero() (gas: 92188)
+InsecureSgxVerifierTest:test_verifyProof_RevertWhen_BadSignature() (gas: 96545)
+InsecureSgxVerifierTest:test_verifyProof_RevertWhen_Expired() (gas: 93590)
+InsecureSgxVerifierTest:test_verifyProof_RevertWhen_InstanceMismatch() (gas: 91823)
+InsecureSgxVerifierTest:test_verifyProof_RevertWhen_InstanceZero() (gas: 9999)
+InsecureSgxVerifierTest:test_verifyProof_RevertWhen_MrEnclaveUntrustedAfterRegistration() (gas: 184293)
+InsecureSgxVerifierTest:test_verifyProof_RevertWhen_MrSignerUntrustedAfterRegistration() (gas: 184514)
 InsecureSgxVerifierTest:test_verifyProof_RevertWhen_WrongLength() (gas: 9094)
-InsecureSgxVerifierTest:test_verifyProof_succeeds() (gas: 95767)
+InsecureSgxVerifierTest:test_verifyProof_succeeds() (gas: 96019)
 LibBlobsTest:test_propose_RevertWhen_BlobNotFound() (gas: 35373)
 LibBlobsTest:test_propose_RevertWhen_NoBlobsProvided() (gas: 34875)
 LibCodecTest:testFuzz_encodeDecodeProposeInput_PreservesFields(uint48,uint16,uint16,uint24,uint16) (runs: 200, μ: 8303, ~: 8303)
@@ -214,37 +215,38 @@ SP1VerifierTest:test_verifyProof_RevertWhen_BlockProgramNotTrusted() (gas: 38407
 SP1VerifierTest:test_verifyProof_RevertWhen_ProofTooShort() (gas: 8903)
 SP1VerifierTest:test_verifyProof_RevertWhen_RemoteVerifierFails() (gas: 64245)
 SP1VerifierTest:test_verifyProof_Succeeds() (gas: 64318)
-SecureSgxVerifierTest:test_addInstances_IgnoresValidityDelay() (gas: 88906)
-SecureSgxVerifierTest:test_addInstances_RecordsNoMrEnclave() (gas: 89350)
-SecureSgxVerifierTest:test_addInstances_RevertWhen_DuplicateAddress() (gas: 91349)
-SecureSgxVerifierTest:test_addInstances_RevertWhen_NotOwner() (gas: 13761)
-SecureSgxVerifierTest:test_addInstances_RevertWhen_ZeroAddress() (gas: 36481)
-SecureSgxVerifierTest:test_addInstances_succeeds() (gas: 143838)
-SecureSgxVerifierTest:test_constructor_RevertWhen_ChainIdZero() (gas: 86771)
-SecureSgxVerifierTest:test_constructor_RevertWhen_ValidityDelayTooLarge() (gas: 116785)
-SecureSgxVerifierTest:test_constructor_RevertWhen_ValidityDelayZero() (gas: 111140)
+SecureSgxVerifierTest:test_addInstances_IgnoresValidityDelay() (gas: 89110)
+SecureSgxVerifierTest:test_addInstances_RecordsNoMrEnclave() (gas: 89554)
+SecureSgxVerifierTest:test_addInstances_RevertWhen_DuplicateAddress() (gas: 91633)
+SecureSgxVerifierTest:test_addInstances_RevertWhen_InstanceIdOverflows() (gas: 223935)
+SecureSgxVerifierTest:test_addInstances_RevertWhen_NotOwner() (gas: 13841)
+SecureSgxVerifierTest:test_addInstances_RevertWhen_ZeroAddress() (gas: 36561)
+SecureSgxVerifierTest:test_addInstances_succeeds() (gas: 144122)
+SecureSgxVerifierTest:test_constructor_RevertWhen_ChainIdZero() (gas: 86780)
+SecureSgxVerifierTest:test_constructor_RevertWhen_ValidityDelayTooLarge() (gas: 116794)
+SecureSgxVerifierTest:test_constructor_RevertWhen_ValidityDelayZero() (gas: 111149)
 SecureSgxVerifierTest:test_constructor_enablesLocalReportCheckByDefault() (gas: 10586)
 SecureSgxVerifierTest:test_deleteInstances_RevertWhen_InvalidInstance() (gas: 13553)
 SecureSgxVerifierTest:test_deleteInstances_RevertWhen_NotOwner() (gas: 11700)
-SecureSgxVerifierTest:test_deleteInstances_succeeds() (gas: 74880)
+SecureSgxVerifierTest:test_deleteInstances_succeeds() (gas: 75084)
 SecureSgxVerifierTest:test_isTcbStatusAccepted_StrictPolicy() (gas: 18394)
 SecureSgxVerifierTest:test_isTcbStatusAccepted_StrictPolicyIsExact() (gas: 407813)
-SecureSgxVerifierTest:test_registerInstance_AllowsDebugBitOutsideFlagsByte() (gas: 174274)
-SecureSgxVerifierTest:test_registerInstance_AllowsRegistrarWhenSet() (gas: 2006162)
-SecureSgxVerifierTest:test_registerInstance_AppliesValidityDelay() (gas: 176639)
-SecureSgxVerifierTest:test_registerInstance_OwnerSkipsValidityDelay() (gas: 176037)
-SecureSgxVerifierTest:test_registerInstance_RecordsMrEnclave() (gas: 176450)
-SecureSgxVerifierTest:test_registerInstance_RecordsPolicyVersion() (gas: 177970)
+SecureSgxVerifierTest:test_registerInstance_AllowsDebugBitOutsideFlagsByte() (gas: 174400)
+SecureSgxVerifierTest:test_registerInstance_AllowsRegistrarWhenSet() (gas: 2014104)
+SecureSgxVerifierTest:test_registerInstance_AppliesValidityDelay() (gas: 176765)
+SecureSgxVerifierTest:test_registerInstance_OwnerSkipsValidityDelay() (gas: 176163)
+SecureSgxVerifierTest:test_registerInstance_RecordsMrEnclave() (gas: 176576)
+SecureSgxVerifierTest:test_registerInstance_RecordsPolicyVersion() (gas: 178182)
 SecureSgxVerifierTest:test_registerInstance_RevertWhen_AllowlistOnAndMrEnclaveUntrusted() (gas: 55662)
 SecureSgxVerifierTest:test_registerInstance_RevertWhen_AllowlistOnAndMrSignerUntrusted() (gas: 38652)
 SecureSgxVerifierTest:test_registerInstance_RevertWhen_AttributesViolateStrictPolicy() (gas: 72641)
-SecureSgxVerifierTest:test_registerInstance_RevertWhen_CallerNotRegistrar() (gas: 1851958)
+SecureSgxVerifierTest:test_registerInstance_RevertWhen_CallerNotRegistrar() (gas: 1859774)
 SecureSgxVerifierTest:test_registerInstance_RevertWhen_DebugEnclave() (gas: 20582)
-SecureSgxVerifierTest:test_registerInstance_RevertWhen_DuplicateInstance() (gas: 185175)
+SecureSgxVerifierTest:test_registerInstance_RevertWhen_DuplicateInstance() (gas: 185324)
 SecureSgxVerifierTest:test_registerInstance_RevertWhen_EnclaveAttributesNotConfigured() (gas: 24243)
 SecureSgxVerifierTest:test_registerInstance_RevertWhen_InstanceZeroAddress() (gas: 85094)
 SecureSgxVerifierTest:test_registerInstance_RevertWhen_LaunchKeyEnabled() (gas: 21975)
-SecureSgxVerifierTest:test_registerInstance_RevertWhen_NoAttestationEntrypoint() (gas: 1851624)
+SecureSgxVerifierTest:test_registerInstance_RevertWhen_NoAttestationEntrypoint() (gas: 1859440)
 SecureSgxVerifierTest:test_registerInstance_RevertWhen_NotVerified() (gas: 18365)
 SecureSgxVerifierTest:test_registerInstance_RevertWhen_OutputTooShort() (gas: 18474)
 SecureSgxVerifierTest:test_registerInstance_RevertWhen_ProvisionKeyEnabled() (gas: 21950)
@@ -253,21 +255,21 @@ SecureSgxVerifierTest:test_registerInstance_RevertWhen_TcbConfigNeeded() (gas: 1
 SecureSgxVerifierTest:test_registerInstance_RevertWhen_TcbOutOfDate() (gas: 19739)
 SecureSgxVerifierTest:test_registerInstance_RevertWhen_TcbOutOfDateConfigNeeded() (gas: 19849)
 SecureSgxVerifierTest:test_registerInstance_RevertWhen_TcbRevoked() (gas: 19782)
-SecureSgxVerifierTest:test_registerInstance_RevertWhen_TcbUnrecognized() (gas: 19783)
+SecureSgxVerifierTest:test_registerInstance_RevertWhen_TcbUnrecognized() (gas: 19761)
 SecureSgxVerifierTest:test_registerInstance_RevertWhen_VerifiedBodyMismatch() (gas: 20589)
 SecureSgxVerifierTest:test_registerInstance_RevertWhen_WrongBodyType() (gas: 19567)
-SecureSgxVerifierTest:test_registerInstance_RevertWhen_WrongQuoteVersion() (gas: 19349)
-SecureSgxVerifierTest:test_registerInstance_SucceedsWhen_AttributesMatchStrictPolicy() (gas: 218328)
-SecureSgxVerifierTest:test_registerInstance_WithAllowlist_succeeds() (gas: 175325)
-SecureSgxVerifierTest:test_registerInstance_acceptsAllAllowedTcbStatuses() (gas: 387551)
-SecureSgxVerifierTest:test_registerInstance_doesNotForwardValue() (gas: 176481)
-SecureSgxVerifierTest:test_registerInstance_succeeds() (gas: 182473)
-SecureSgxVerifierTest:test_removeEnclaveAttributePolicy_ByRegistrar() (gas: 1835403)
+SecureSgxVerifierTest:test_registerInstance_RevertWhen_WrongQuoteVersion() (gas: 19372)
+SecureSgxVerifierTest:test_registerInstance_SucceedsWhen_AttributesMatchStrictPolicy() (gas: 218454)
+SecureSgxVerifierTest:test_registerInstance_WithAllowlist_succeeds() (gas: 175451)
+SecureSgxVerifierTest:test_registerInstance_acceptsAllAllowedTcbStatuses() (gas: 387929)
+SecureSgxVerifierTest:test_registerInstance_doesNotForwardValue() (gas: 176563)
+SecureSgxVerifierTest:test_registerInstance_succeeds() (gas: 182599)
+SecureSgxVerifierTest:test_removeEnclaveAttributePolicy_ByRegistrar() (gas: 1843219)
 SecureSgxVerifierTest:test_removeEnclaveAttributePolicy_FailsClosedAfterRemoval() (gas: 59120)
 SecureSgxVerifierTest:test_removeEnclaveAttributePolicy_RevertWhen_NoRegistrarConfigured() (gas: 59396)
-SecureSgxVerifierTest:test_removeEnclaveAttributePolicy_RevertWhen_NotOwnerOrRegistrar() (gas: 1850527)
+SecureSgxVerifierTest:test_removeEnclaveAttributePolicy_RevertWhen_NotOwnerOrRegistrar() (gas: 1858343)
 SecureSgxVerifierTest:test_setEnclaveAttributePolicy_BumpsVersionOnEverySet() (gas: 75706)
-SecureSgxVerifierTest:test_setEnclaveAttributePolicy_RevertWhen_CalledByRegistrar() (gas: 1802637)
+SecureSgxVerifierTest:test_setEnclaveAttributePolicy_RevertWhen_CalledByRegistrar() (gas: 1810453)
 SecureSgxVerifierTest:test_setEnclaveAttributePolicy_RevertWhen_ExpectedHasForbiddenBit() (gas: 11280)
 SecureSgxVerifierTest:test_setEnclaveAttributePolicy_RevertWhen_ExpectedOutsideMask() (gas: 11146)
 SecureSgxVerifierTest:test_setEnclaveAttributePolicy_RevertWhen_MaskMissesForbiddenBit() (gas: 11201)
@@ -280,24 +282,24 @@ SecureSgxVerifierTest:test_setMrSigner_setsAndEmits() (gas: 37241)
 SecureSgxVerifierTest:test_tcbStatusEnum_matchesExpectedValues() (gas: 6282)
 SecureSgxVerifierTest:test_toggleLocalReportCheck_RevertWhen_NotOwner() (gas: 11047)
 SecureSgxVerifierTest:test_toggleLocalReportCheck_togglesAndEmits() (gas: 21045)
-SecureSgxVerifierTest:test_verifyProof_AllowlistDisabledSkipsReCheck() (gas: 166629)
-SecureSgxVerifierTest:test_verifyProof_OwnerAddedInstanceIgnoresAllowlistChanges() (gas: 107855)
-SecureSgxVerifierTest:test_verifyProof_RevertWhen_AggregatedHashZero() (gas: 91986)
-SecureSgxVerifierTest:test_verifyProof_RevertWhen_BadSignature() (gas: 96409)
-SecureSgxVerifierTest:test_verifyProof_RevertWhen_Expired() (gas: 93388)
-SecureSgxVerifierTest:test_verifyProof_RevertWhen_InstanceMismatch() (gas: 91729)
+SecureSgxVerifierTest:test_verifyProof_AllowlistDisabledSkipsReCheck() (gas: 166755)
+SecureSgxVerifierTest:test_verifyProof_OwnerAddedInstanceIgnoresAllowlistChanges() (gas: 108059)
+SecureSgxVerifierTest:test_verifyProof_RevertWhen_AggregatedHashZero() (gas: 92190)
+SecureSgxVerifierTest:test_verifyProof_RevertWhen_BadSignature() (gas: 96613)
+SecureSgxVerifierTest:test_verifyProof_RevertWhen_Expired() (gas: 93592)
+SecureSgxVerifierTest:test_verifyProof_RevertWhen_InstanceMismatch() (gas: 91889)
 SecureSgxVerifierTest:test_verifyProof_RevertWhen_InstanceZero() (gas: 10044)
-SecureSgxVerifierTest:test_verifyProof_RevertWhen_MrEnclaveUntrustedAfterRegistration() (gas: 187205)
-SecureSgxVerifierTest:test_verifyProof_RevertWhen_MrSignerUntrustedAfterRegistration() (gas: 170335)
-SecureSgxVerifierTest:test_verifyProof_RevertWhen_PolicyEditedInPlace() (gas: 191425)
-SecureSgxVerifierTest:test_verifyProof_RevertWhen_PolicyRemovedBeforeDelayElapses() (gas: 181300)
-SecureSgxVerifierTest:test_verifyProof_RevertWhen_PolicyRemovedForValidInstance() (gas: 190317)
-SecureSgxVerifierTest:test_verifyProof_RevertWhen_PolicyRemovedThenReAdded() (gas: 196123)
-SecureSgxVerifierTest:test_verifyProof_RevertWhen_RegistrarRemovesPolicy() (gas: 1991480)
-SecureSgxVerifierTest:test_verifyProof_RevertWhen_WithinValidityDelay() (gas: 188372)
+SecureSgxVerifierTest:test_verifyProof_RevertWhen_MrEnclaveUntrustedAfterRegistration() (gas: 187331)
+SecureSgxVerifierTest:test_verifyProof_RevertWhen_MrSignerUntrustedAfterRegistration() (gas: 170461)
+SecureSgxVerifierTest:test_verifyProof_RevertWhen_PolicyEditedInPlace() (gas: 191551)
+SecureSgxVerifierTest:test_verifyProof_RevertWhen_PolicyRemovedBeforeDelayElapses() (gas: 181426)
+SecureSgxVerifierTest:test_verifyProof_RevertWhen_PolicyRemovedForValidInstance() (gas: 190443)
+SecureSgxVerifierTest:test_verifyProof_RevertWhen_PolicyRemovedThenReAdded() (gas: 196249)
+SecureSgxVerifierTest:test_verifyProof_RevertWhen_RegistrarRemovesPolicy() (gas: 1999422)
+SecureSgxVerifierTest:test_verifyProof_RevertWhen_WithinValidityDelay() (gas: 188498)
 SecureSgxVerifierTest:test_verifyProof_RevertWhen_WrongLength() (gas: 9117)
-SecureSgxVerifierTest:test_verifyProof_SucceedsForNewInstanceAfterReauthorization() (gas: 303030)
-SecureSgxVerifierTest:test_verifyProof_succeeds() (gas: 95949)
+SecureSgxVerifierTest:test_verifyProof_SucceedsForNewInstanceAfterReauthorization() (gas: 303282)
+SecureSgxVerifierTest:test_verifyProof_succeeds() (gas: 96153)
 TestLibPreconfUtils:test_getBeaconBlockRootAtOrAfter() (gas: 90591)
 TestMainnetDAOController:test_MainnetDAOController_InitialOwner() (gas: 17990)
 TestMainnetDAOController:test_MainnetDAOController_acceptOwnershipOf() (gas: 45395)
```

### packages/protocol/test/layer1/verifiers/SgxVerifier.t.sol
```diff
@@ -2,6 +2,7 @@
 pragma solidity ^0.8.24;
 
 import { TCBStatus } from "@automata-network/on-chain-pccs/helpers/FmspcTcbHelper.sol";
+import { StdStorage, stdStorage } from "forge-std/src/StdStorage.sol";
 import "forge-std/src/Test.sol";
 import { IDcapAttestation } from "src/layer1/verifiers/IDcapAttestation.sol";
 import { InsecureSgxVerifier } from "src/layer1/verifiers/InsecureSgxVerifier.sol";
@@ -19,6 +20,8 @@ import { SgxVerifier } from "src/layer1/verifiers/SgxVerifier.sol";
 /// TCB-status and ATTRIBUTES-pin behaviour is asserted in the subclasses below.
 /// @custom:security-contact security@taiko.xyz
 abstract contract SgxVerifierTestBase is Test {
+    using stdStorage for StdStorage;
+
     uint64 internal constant CHAIN_ID = 167;
     address internal constant ATTESTATION = address(0xA11CE);
 
@@ -527,6 +530,26 @@ abstract contract SgxVerifierTestBase is Test {
         verifier.addInstances(addrs);
     }
 
+    /// @dev The last id that still fits the uint32 field decoded in `verifyProof` registers; the
+    /// next one would overflow that field and be unreachable from a proof, so it is rejected.
+    function test_addInstances_RevertWhen_InstanceIdOverflows() external {
+        // Fast-forward the id counter to the largest uint32-representable id.
+        stdstore.target(address(verifier)).sig("nextInstanceId()")
+            .checked_write(uint256(type(uint32).max));
+
+        // id == type(uint32).max still fits the uint32 proof field and is accepted.
+        address[] memory addrs = new address[](1);
+        addrs[0] = address(0xA1);
+        uint256[] memory ids = verifier.addInstances(addrs);
+        assertEq(ids[0], uint256(type(uint32).max));
+        assertEq(verifier.nextInstanceId(), uint256(type(uint32).max) + 1);
+
+        // The next id (2^32) would truncate to 0 in `verifyProof`; registration must reject it.
+        addrs[0] = address(0xA2);
+        vm.expectRevert(SgxVerifier.SGX_INSTANCE_ID_OVERFLOW.selector);
+        verifier.addInstances(addrs);
+    }
+
     function test_deleteInstances_succeeds() external {
         address[] memory addrs = new address[](1);
         addrs[0] = address(0xA1);
```
