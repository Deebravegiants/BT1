# [?] fix: Remove redundant Close() call which results in panic (#3334)

## Summary
Severity: Unknown
Chain: Starknet
Component: NethermindEth/juno
Published: 2025-12-17
Source: https://github.com/NethermindEth/juno/commit/080aafd9e675ab2a06c21269d7663201cdae1740
Type: security-commit

## Details
fix: Remove redundant Close() call which results in panic (#3334)

## Patch
### db/typed/prefix/bucket.go
```diff
@@ -53,7 +53,6 @@ func (b *PrefixedBucket[T, K, V, KS, VS]) scan( //nolint:unused // False positiv
 		}
 
 		isExited, err := iterate[V, VS](it, yield)
-		err = utils.RunAndWrapOnError(it.Close, err)
 		if err := utils.RunAndWrapOnError(it.Close, err); !isExited && err != nil {
 			yield(Entry[V]{}, err)
 		}
```

### db/typed/prefix/bucket_test.go
```diff
@@ -5,13 +5,15 @@ import (
 	cryptorand "crypto/rand"
 	"iter"
 	"maps"
+	"math"
 	"math/rand/v2"
 	"slices"
+	"sync"
 	"testing"
 
 	"github.com/NethermindEth/juno/core/felt"
 	"github.com/NethermindEth/juno/db"
-	"github.com/NethermindEth/juno/db/memory"
+	"github.com/NethermindEth/juno/db/pebble"
 	"github.com/NethermindEth/juno/db/typed"
 	"github.com/NethermindEth/juno/db/typed/key"
 	"github.com/NethermindEth/juno/db/typed/prefix"
@@ -113,6 +115,27 @@ func filter[K comparable, V any](filter *K, cmp func(K, K) int, entries map[K]V)
 	}
 }
 
+func takeN[A any, B any](t *testing.T, seq iter.Seq2[A, B], n int) iter.Seq2[A, B] {
+	return func(yield func(A, B) bool) {
+		if n == 0 {
+			return
+		}
+
+		count := 0
+		for a, b := range seq {
+			if !yield(a, b) {
+				return
+			}
+			count++
+			if count == n {
+				return
+			}
+		}
+
+		require.FailNow(t, "not enough elements")
+	}
+}
+
 func randomEntry[K comparable, V any](t *testing.T, entries map[K]V) (K, V) {
 	t.Helper()
 	for key, value := range entries {
@@ -163,16 +186,25 @@ func randomDeletedRange[K comparable, V any](
 func validateResult(
 	t *testing.T,
 	expected []testEntry,
+	expectedErr bool,
 	actual iter.Seq2[prefix.Entry[felt.ClassHash], error],
 ) {
 	t.Helper()
 	count := 0
 	for entry, err := range actual {
-		require.NoError(t, err)
-		require.Greater(t, len(expected), count)
-		require.Equal(t, bucket.Key(expected[count].key.Marshal()), entry.Key)
-		require.Equal(t, expected[count].value, entry.Value)
-		count++
+		if count < len(expected) {
+			require.NoError(t, err)
+			require.Greater(t, len(expected), count)
+			require.Equal(t, bucket.Key(expected[count].key.Marshal()), entry.Key)
+			require.Equal(t, expected[count].value, entry.Value)
+			count++
+		} else {
+			if !expectedErr {
+				require.FailNow(t, "not expect error, but got more entries than expected")
+			} else {
+				require.Error(t, err)
+			}
+		}
 	}
 	require.Equal(t, len(expected), count)
 }
@@ -181,11 +213,13 @@ func testFullScan(
 	t *testing.T,
 	database db.KeyValueReader,
 	content entryMap,
+	expectedErr bool,
 ) {
 	t.Helper()
 	validateResult(
 		t,
 		extractExpectedEntries(content, nil, nil, nil),
+		expectedErr,
 		bucket.Prefix().Scan(database),
 	)
 }
@@ -194,12 +228,14 @@ func test1LayerScan(
 	t *testing.T,
 	database db.KeyValueReader,
 	content entryMap,
+	expectedErr bool,
 	blockNumber uint64,
 ) {
 	t.Helper()
 	validateResult(
 		t,
 		extractExpectedEntries(content, &blockNumber, nil, nil),
+		expectedErr,
 		bucket.Prefix().Add(blockNumber).Scan(database),
 	)
 }
@@ -208,13 +244,15 @@ func test2LayerScan(
 	t *testing.T,
 	database db.KeyValueReader,
 	content entryMap,
+	expectedErr bool,
 	blockNumber uint64,
 	address felt.Address,
 ) {
 	t.Helper()
 	validateResult(
 		t,
 		extractExpectedEntries(content, &blockNumber, &address, nil),
+		expectedErr,
 		bucket.Prefix().Add(blockNumber).Add(&address).Scan(database),
 	)
 }
@@ -223,6 +261,7 @@ func test3LayerScan(
 	t *testing.T,
 	database db.KeyValueReader,
 	content entryMap,
+	expectedErr bool,
 	blockNumber uint64,
 	address felt.Address,
 	slot string,
@@ -231,6 +270,7 @@ func test3LayerScan(
 	validateResult(
 		t,
 		extractExpectedEntries(content, &blockNumber, &address, &slot),
+		expectedErr,
 		bucket.Prefix().Add(blockNumber).Add(&address).Add([]byte(slot)).Scan(database),
 	)
 }
@@ -243,21 +283,21 @@ func runReadTests(
 	t.Helper()
 
 	t.Run("Full scan", func(t *testing.T) {
-		testFullScan(t, database, content)
+		testFullScan(t, database, content, false)
 	})
 
 	t.Run("1 layer scan", func(t *testing.T) {
 		for range readTestsPerLayer {
 			blockNumber, _ := randomEntry(t, content)
-			test1LayerScan(t, database, content, blockNumber)
+			test1LayerScan(t, database, content, false, blockNumber)
 		}
 	})
 
 	t.Run("2 layer scan", func(t *testing.T) {
 		for range readTestsPerLayer * readTestsPerLayer {
 			blockNumber, map1 := randomEntry(t, content)
 			hash, _ := randomEntry(t, map1)
-			test2LayerScan(t, database, content, blockNumber, hash)
+			test2LayerScan(t, database, content, false, blockNumber, hash)
 		}
 	})
 
@@ -266,43 +306,74 @@ func runReadTests(
 			blockNumber, map1 := randomEntry(t, content)
 			hash, map2 := randomEntry(t, map1)
 			slot, _ := randomEntry(t, map2)
-			test3LayerScan(t, database, content, blockNumber, hash, slot)
+			test3LayerScan(t, database, content, false, blockNumber, hash, slot)
 		}
 	})
 }
 
-func TestPrefixedBucket(t *testing.T) {
-	database := memory.New()
-	content := make(entryMap)
+func createNewDatabase(t *testing.T) (db.KeyValueStore, entryMap) {
+	t.Helper()
+	database, err := pebble.New(t.TempDir())
+	require.NoError(t, err)
+	return database, make(entryMap)
+}
+
+func populateDatabase(
+	t *testing.T,
+	database db.KeyValueWriter,
+	content entryMap,
+	layerKeyCount int,
+) {
+	t.Helper()
+	for range layerKeyCount {
+		blockNumber := rand.Uint64()
+		content[blockNumber] = make(map[felt.Address]map[string]testEntry, layerKeyCount)
 
-	t.Run("Populate database", func(t *testing.T) {
 		for range layerKeyCount {
-			blockNumber := rand.Uint64()
-			content[blockNumber] = make(map[felt.Address]map[string]testEntry)
+			address := felt.Random[felt.Address]()
+			content[blockNumber][address] = make(map[string]testEntry, layerKeyCount)
 
 			for range layerKeyCount {
-				address := felt.Random[felt.Address]()
-				content[blockNumber][address] = make(map[string]testEntry)
-
-				for range layerKeyCount {
-					slot := cryptorand.Text()
-					value := felt.Random[felt.ClassHash]()
-
-					key := testKey{
-						number:  blockNumber,
-						address: address,
-						slot:    []byte(slot),
-					}
-					entry := testEntry{
-						key:   key,
-						value: value,
-					}
+				slot := cryptorand.Text()
+				value := felt.Random[felt.ClassHash]()
 
-					content[blockNumber][address][slot] = entry
-					require.NoError(t, bucket.Put(database, key, &value))
+				key := testKey{
+					number:  blockNumber,
+					address: address,
+					slot:    []byte(slot),
 				}
+				entry := testEntry{
+					key:   key,
+					value: value,
+				}
+
+				content[blockNumber][address][slot] = entry
+				require.NoError(t, bucket.Put(database, key, &value))
 			}
 		}
+	}
+}
+
+func insertInvalidValue(t *testing.T, database db.KeyValueWriter) testKey {
+	// max felt === -1 mod module
+	maxFelt := new(felt.Felt).Sub(&felt.Zero, &felt.One)
+	t.Helper()
+	lastKey := testKey{
+		number:  math.MaxUint64,
+		address: felt.Address(*maxFelt),
+		slot:    []byte(cryptorand.Text()),
+	}
+	invalidValue := []byte("invalid felt")
+	require.NoError(t, bucket.RawValue().Put(database, lastKey, &invalidValue))
+	return lastKey
+}
+
+func TestPrefixedBucket(t *testing.T) {
+	database, content := createNewDatabase(t)
+	defer database.Close()
+
+	t.Run("Populate database", func(t *testing.T) {
+		populateDatabase(t, database, content, layerKeyCount)
 	})
 
 	t.Run("Scan", func(t *testing.T) {
@@ -321,10 +392,10 @@ func TestPrefixedBucket(t *testing.T) {
 						database,
 					),
 				)
-				test3LayerScan(t, database, content, blockNumber, hash, slot)
-				test2LayerScan(t, database, content, blockNumber, hash)
-				test1LayerScan(t, database, content, blockNumber)
-				testFullScan(t, database, content)
+				test3LayerScan(t, database, content, false, blockNumber, hash, slot)
+				test2LayerScan(t, database, content, false, blockNumber, hash)
+				test1LayerScan(t, database, content, false, blockNumber)
+				testFullScan(t, database, content, false)
 			}
 		})
 
@@ -336,23 +407,23 @@ func TestPrefixedBucket(t *testing.T) {
 					t,
 					bucket.Prefix().Add(blockNumber).Add(&hash).DeletePrefix(database),
 				)
-				test2LayerScan(t, database, content, blockNumber, hash)
-				test1LayerScan(t, database, content, blockNumber)
-				testFullScan(t, database, content)
+				test2LayerScan(t, database, content, false, blockNumber, hash)
+				test1LayerScan(t, database, content, false, blockNumber)
+				testFullScan(t, database, content, false)
 			}
 		})
 
 		t.Run("Layer 1", func(t *testing.T) {
 			for range deleteTests {
 				blockNumber := randomDeletedKey(t, content)
 				require.NoError(t, bucket.Prefix().Add(blockNumber).DeletePrefix(database))
-				test1LayerScan(t, database, content, blockNumber)
-				testFullScan(t, database, content)
+				test1LayerScan(t, database, content, false, blockNumber)
+				testFullScan(t, database, content, false)
 			}
 		})
 
 		t.Run("Run full scan after delete", func(t *testing.T) {
-			testFullScan(t, database, content)
+			testFullScan(t, database, content, false)
 		})
 	})
 
@@ -370,11 +441,11 @@ func TestPrefixedBucket(t *testing.T) {
 						[]byte(upperBound),
 					),
 				)
-				test3LayerScan(t, database, content, blockNumber, hash, lowerBound)
-				test3LayerScan(t, database, content, blockNumber, hash, upperBound)
-				test2LayerScan(t, database, content, blockNumber, hash)
-				test1LayerScan(t, database, content, blockNumber)
-				testFullScan(t, database, content)
+				test3LayerScan(t, database, content, false, blockNumber, hash, lowerBound)
+				test3LayerScan(t, database, content, false, blockNumber, hash, upperBound)
+				test2LayerScan(t, database, content, false, blockNumber, hash)
+				test1LayerScan(t, database, content, false, blockNumber)
+				testFullScan(t, database, content, false)
 			}
 		})
 
@@ -387,10 +458,10 @@ func TestPrefixedBucket(t *testing.T) {
 					&lowerBound,
 					&upperBound,
 				))
-				test2LayerScan(t, database, content, blockNumber, lowerBound)
-				test2LayerScan(t, database, content, blockNumber, upperBound)
-				test1LayerScan(t, database, content, blockNumber)
-				testFullScan(t, database, content)
+				test2LayerScan(t, database, content, false, blockNumber, lowerBound)
+				test2LayerScan(t, database, content, false, blockNumber, upperBound)
+				test1LayerScan(t, database, content, false, blockNumber)
+				testFullScan(t, database, content, false)
 			}
 		})
 
@@ -402,14 +473,61 @@ func TestPrefixedBucket(t *testing.T) {
 					lowerBound,
 					upperBound,
 				))
-				test1LayerScan(t, database, content, lowerBound)
-				test1LayerScan(t, database, content, upperBound)
-				testFullScan(t, database, content)
+				test1LayerScan(t, database, content, false, lowerBound)
+				test1LayerScan(t, database, content, false, upperBound)
+				testFullScan(t, database, content, false)
 			}
 		})
 
 		t.Run("Run full scan after delete", func(t *testing.T) {
-			testFullScan(t, database, content)
+			testFullScan(t, database, content, false)
 		})
 	})
+
+	t.Run("Break case", func(t *testing.T) {
+		entries := extractExpectedEntries(content, nil, nil, nil)
+		breakpoint := len(entries) / 2
+		validateResult(
+			t,
+			entries[:breakpoint],
+			false,
+			takeN(t, bucket.Prefix().Scan(database), breakpoint),
+		)
+	})
+
+	t.Run("Error case", func(t *testing.T) {
+		key := insertInvalidValue(t, database)
+		test3LayerScan(t, database, content, true, key.number, key.address, string(key.slot))
+		test2LayerScan(t, database, content, true, key.number, key.address)
+		test1LayerScan(t, database, content, true, key.number)
+		testFullScan(t, database, content, true)
+	})
+}
+
+func TestLeakyClose(t *testing.T) {
+	t.Parallel()
+	for _, expectErr := range []bool{true, false} {
+		name := "No error"
+		if expectErr {
+			name = "Error"
+		}
+		t.Run(name, func(t *testing.T) {
+			t.Parallel()
+			database, content := createNewDatabase(t)
+			populateDatabase(t, database, content, 1)
+
+			if expectErr {
+				insertInvalidValue(t, database)
+			}
+			wg := sync.WaitGroup{}
+			t.Cleanup(wg.Wait)
+			for range 32 {
+				wg.Go(func() {
+					for range 10000 {
+						testFullScan(t, database, content, expectErr)
+					}
+				})
+			}
+		})
+	}
 }
```
