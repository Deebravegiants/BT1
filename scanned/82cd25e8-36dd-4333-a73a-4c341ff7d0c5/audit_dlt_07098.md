# [?] Initialise slasher service using New in slasher test to avoid panics (#11046)

## Summary
Severity: Unknown
Chain: Ethereum
Component: prysmaticlabs/prysm
Published: 2022-07-26
Source: https://github.com/OffchainLabs/prysm/commit/5a4edf897fece680831a90d6bf997e92468d3b3e
Type: security-commit

## Details
Initialise slasher service using New in slasher test to avoid panics (#11046)

* Initialise slasher service using New in slasher test to avoid panics

* Handle unhanlded error

Co-authored-by: Radosław Kapka <rkapka@wp.pl>
Co-authored-by: Preston Van Loon <preston@prysmaticlabs.com>

## Patch
### beacon-chain/slasher/detect_attestations_test.go
```diff
@@ -232,19 +232,17 @@ func Test_processQueuedAttestations(t *testing.T) {
 				attestationWrapper.IndexedAttestation.Signature = bls.AggregateSignatures(sigs).Marshal()
 			}
 
-			s := &Service{
-				serviceCfg: &ServiceConfig{
+			s, err := New(context.Background(),
+				&ServiceConfig{
 					Database:                slasherDB,
 					StateNotifier:           &mock.MockStateNotifier{},
 					HeadStateFetcher:        mockChain,
 					AttestationStateFetcher: mockChain,
 					SlashingPoolInserter:    &slashingsmock.PoolMock{},
-				},
-				params:                         DefaultParams(),
-				attsQueue:                      newAttestationsQueue(),
-				genesisTime:                    genesisTime,
-				latestEpochWrittenForValidator: map[types.ValidatorIndex]types.Epoch{},
-			}
+				})
+			require.NoError(t, err)
+			s.genesisTime = genesisTime
+
 			currentSlotChan := make(chan types.Slot)
 			exitChan := make(chan struct{})
 			go func() {
@@ -291,19 +289,17 @@ func Test_processQueuedAttestations_MultipleChunkIndices(t *testing.T) {
 		State: beaconState,
 	}
 
-	s := &Service{
-		serviceCfg: &ServiceConfig{
+	s, err := New(context.Background(),
+		&ServiceConfig{
 			Database:                slasherDB,
 			StateNotifier:           &mock.MockStateNotifier{},
 			HeadStateFetcher:        mockChain,
 			AttestationStateFetcher: mockChain,
 			SlashingPoolInserter:    &slashingsmock.PoolMock{},
-		},
-		params:                         slasherParams,
-		attsQueue:                      newAttestationsQueue(),
-		genesisTime:                    genesisTime,
-		latestEpochWrittenForValidator: map[types.ValidatorIndex]types.Epoch{},
-	}
+		})
+	require.NoError(t, err)
+	s.genesisTime = genesisTime
+
 	currentSlotChan := make(chan types.Slot)
 	exitChan := make(chan struct{})
 	go func() {
@@ -358,19 +354,17 @@ func Test_processQueuedAttestations_OverlappingChunkIndices(t *testing.T) {
 		State: beaconState,
 	}
 
-	s := &Service{
-		serviceCfg: &ServiceConfig{
+	s, err := New(context.Background(),
+		&ServiceConfig{
 			Database:                slasherDB,
 			StateNotifier:           &mock.MockStateNotifier{},
 			HeadStateFetcher:        mockChain,
 			AttestationStateFetcher: mockChain,
 			SlashingPoolInserter:    &slashingsmock.PoolMock{},
-		},
-		params:                         slasherParams,
-		attsQueue:                      newAttestationsQueue(),
-		genesisTime:                    genesisTime,
-		latestEpochWrittenForValidator: map[types.ValidatorIndex]types.Epoch{},
-	}
+		})
+	require.NoError(t, err)
+	s.genesisTime = genesisTime
+
 	currentSlotChan := make(chan types.Slot)
 	exitChan := make(chan struct{})
 	go func() {
@@ -477,14 +471,13 @@ func Test_applyAttestationForValidator_MinSpanChunk(t *testing.T) {
 	ctx := context.Background()
 	slasherDB := dbtest.SetupSlasherDB(t)
 	defaultParams := DefaultParams()
-	srv := &Service{
-		params: defaultParams,
-		serviceCfg: &ServiceConfig{
+	srv, err := New(context.Background(),
+		&ServiceConfig{
 			Database:      slasherDB,
 			StateNotifier: &mock.MockStateNotifier{},
-		},
-		latestEpochWrittenForValidator: map[types.ValidatorIndex]types.Epoch{},
-	}
+		})
+	require.NoError(t, err)
+
 	// We initialize an empty chunks slice.
 	chunk := EmptyMinSpanChunksSlice(defaultParams)
 	chunkIdx := uint64(0)
@@ -538,14 +531,13 @@ func Test_applyAttestationForValidator_MaxSpanChunk(t *testing.T) {
 	ctx := context.Background()
 	slasherDB := dbtest.SetupSlasherDB(t)
 	defaultParams := DefaultParams()
-	srv := &Service{
-		params: defaultParams,
-		serviceCfg: &ServiceConfig{
+	srv, err := New(context.Background(),
+		&ServiceConfig{
 			Database:      slasherDB,
 			StateNotifier: &mock.MockStateNotifier{},
-		},
-		latestEpochWrittenForValidator: map[types.ValidatorIndex]types.Epoch{},
-	}
+		})
+	require.NoError(t, err)
+
 	// We initialize an empty chunks slice.
 	chunk := EmptyMaxSpanChunksSlice(defaultParams)
 	chunkIdx := uint64(0)
@@ -606,13 +598,13 @@ func Test_checkDoubleVotes_SlashableInputAttestations(t *testing.T) {
 		createAttestationWrapper(t, 0, 2, []uint64{1, 2}, []byte{1}),
 		createAttestationWrapper(t, 0, 2, []uint64{1, 2}, []byte{2}), // Different signing root.
 	}
-	srv := &Service{
-		serviceCfg: &ServiceConfig{
+	srv, err := New(context.Background(),
+		&ServiceConfig{
 			Database:      slasherDB,
 			StateNotifier: &mock.MockStateNotifier{},
-		},
-		params: DefaultParams(),
-	}
+		})
+	require.NoError(t, err)
+
 	prev1 := createAttestationWrapper(t, 0, 2, []uint64{1, 2}, []byte{1})
 	cur1 := createAttestationWrapper(t, 0, 2, []uint64{1, 2}, []byte{2})
 	prev2 := createAttestationWrapper(t, 0, 2, []uint64{1, 2}, []byte{1})
@@ -642,14 +634,14 @@ func Test_checkDoubleVotes_SlashableAttestationsOnDisk(t *testing.T) {
 		createAttestationWrapper(t, 0, 1, []uint64{1, 2}, []byte{1}),
 		createAttestationWrapper(t, 0, 2, []uint64{1, 2}, []byte{1}),
 	}
-	srv := &Service{
-		serviceCfg: &ServiceConfig{
+	srv, err := New(context.Background(),
+		&ServiceConfig{
 			Database:      slasherDB,
 			StateNotifier: &mock.MockStateNotifier{},
-		},
-		params: DefaultParams(),
-	}
-	err := slasherDB.SaveAttestationRecordsForValidators(ctx, prevAtts)
+		})
+	require.NoError(t, err)
+
+	err = slasherDB.SaveAttestationRecordsForValidators(ctx, prevAtts)
 	require.NoError(t, err)
 
 	prev1 := createAttestationWrapper(t, 0, 2, []uint64{1, 2}, []byte{1})
@@ -687,14 +679,15 @@ func testLoadChunks(t *testing.T, kind slashertypes.ChunkKind) {
 	ctx := context.Background()
 
 	// Check if the chunk at chunk index already exists in-memory.
-	defaultParams := DefaultParams()
-	s := &Service{
-		params: DefaultParams(),
-		serviceCfg: &ServiceConfig{
+	s, err := New(context.Background(),
+		&ServiceConfig{
 			Database:      slasherDB,
 			StateNotifier: &mock.MockStateNotifier{},
-		},
-	}
+		})
+	require.NoError(t, err)
+
+	defaultParams := s.params
+
 	// If a chunk at a chunk index does not exist, ensure it
 	// is initialized as an empty chunk.
 	var emptyChunk Chunker
@@ -771,15 +764,13 @@ func TestService_processQueuedAttestations(t *testing.T) {
 		Slot:  &slot,
 	}
 
-	s := &Service{
-		params: DefaultParams(),
-		serviceCfg: &ServiceConfig{
+	s, err := New(context.Background(),
+		&ServiceConfig{
 			Database:         slasherDB,
 			StateNotifier:    &mock.MockStateNotifier{},
 			HeadStateFetcher: mockChain,
-		},
-		attsQueue: newAttestationsQueue(),
-	}
+		})
+	require.NoError(t, err)
 
 	s.attsQueue.extend([]*slashertypes.IndexedAttestationWrapper{
 		createAttestationWrapper(t, 0, 1, []uint64{0, 1} /* indices */, nil /* signingRoot */),
@@ -810,15 +801,12 @@ func BenchmarkCheckSlashableAttestations(b *testing.B) {
 		Slot:  &slot,
 	}
 
-	s := &Service{
-		params: DefaultParams(),
-		serviceCfg: &ServiceConfig{
-			Database:         slasherDB,
-			StateNotifier:    &mock.MockStateNotifier{},
-			HeadStateFetcher: mockChain,
-		},
-		attsQueue: newAttestationsQueue(),
-	}
+	s, err := New(context.Background(), &ServiceConfig{
+		Database:         slasherDB,
+		StateNotifier:    &mock.MockStateNotifier{},
+		HeadStateFetcher: mockChain,
+	})
+	require.NoError(b, err)
 
 	b.Run("1 attestation 1 validator", func(b *testing.B) {
 		b.ResetTimer()
```
