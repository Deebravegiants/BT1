# [?] Godeps: update goleveldb to fix a compaction data race

## Summary
Severity: Unknown
Chain: Ronin
Component: axieinfinity/ronin-archive
Published: 2016-03-10
Source: https://github.com/axieinfinity/ronin-archive/commit/ea19e61fbaeb29fc9047419cb138d5ca0f2021fc
Type: security-commit

## Details
Godeps: update goleveldb to fix a compaction data race

## Patch
### Godeps/Godeps.json
```diff
@@ -140,51 +140,51 @@
 		},
 		{
 			"ImportPath": "github.com/syndtr/goleveldb/leveldb",
-			"Rev": "e7e6f5b5ef25adb580feac515f9ccec514d0bda8"
+			"Rev": "ad0d8b2ab58a55ed5c58073aa46451d5e1ca1280"
 		},
 		{
 			"ImportPath": "github.com/syndtr/goleveldb/leveldb/cache",
-			"Rev": "e7e6f5b5ef25adb580feac515f9ccec514d0bda8"
+			"Rev": "ad0d8b2ab58a55ed5c58073aa46451d5e1ca1280"
 		},
 		{
 			"ImportPath": "github.com/syndtr/goleveldb/leveldb/comparer",
-			"Rev": "e7e6f5b5ef25adb580feac515f9ccec514d0bda8"
+			"Rev": "ad0d8b2ab58a55ed5c58073aa46451d5e1ca1280"
 		},
 		{
 			"ImportPath": "github.com/syndtr/goleveldb/leveldb/errors",
-			"Rev": "e7e6f5b5ef25adb580feac515f9ccec514d0bda8"
+			"Rev": "ad0d8b2ab58a55ed5c58073aa46451d5e1ca1280"
 		},
 		{
 			"ImportPath": "github.com/syndtr/goleveldb/leveldb/filter",
-			"Rev": "e7e6f5b5ef25adb580feac515f9ccec514d0bda8"
+			"Rev": "ad0d8b2ab58a55ed5c58073aa46451d5e1ca1280"
 		},
 		{
 			"ImportPath": "github.com/syndtr/goleveldb/leveldb/iterator",
-			"Rev": "e7e6f5b5ef25adb580feac515f9ccec514d0bda8"
+			"Rev": "ad0d8b2ab58a55ed5c58073aa46451d5e1ca1280"
 		},
 		{
 			"ImportPath": "github.com/syndtr/goleveldb/leveldb/journal",
-			"Rev": "e7e6f5b5ef25adb580feac515f9ccec514d0bda8"
+			"Rev": "ad0d8b2ab58a55ed5c58073aa46451d5e1ca1280"
 		},
 		{
 			"ImportPath": "github.com/syndtr/goleveldb/leveldb/memdb",
-			"Rev": "e7e6f5b5ef25adb580feac515f9ccec514d0bda8"
+			"Rev": "ad0d8b2ab58a55ed5c58073aa46451d5e1ca1280"
 		},
 		{
 			"ImportPath": "github.com/syndtr/goleveldb/leveldb/opt",
-			"Rev": "e7e6f5b5ef25adb580feac515f9ccec514d0bda8"
+			"Rev": "ad0d8b2ab58a55ed5c58073aa46451d5e1ca1280"
 		},
 		{
 			"ImportPath": "github.com/syndtr/goleveldb/leveldb/storage",
-			"Rev": "e7e6f5b5ef25adb580feac515f9ccec514d0bda8"
+			"Rev": "ad0d8b2ab58a55ed5c58073aa46451d5e1ca1280"
 		},
 		{
 			"ImportPath": "github.com/syndtr/goleveldb/leveldb/table",
-			"Rev": "e7e6f5b5ef25adb580feac515f9ccec514d0bda8"
+			"Rev": "ad0d8b2ab58a55ed5c58073aa46451d5e1ca1280"
 		},
 		{
 			"ImportPath": "github.com/syndtr/goleveldb/leveldb/util",
-			"Rev": "e7e6f5b5ef25adb580feac515f9ccec514d0bda8"
+			"Rev": "ad0d8b2ab58a55ed5c58073aa46451d5e1ca1280"
 		},
 		{
 			"ImportPath": "golang.org/x/crypto/pbkdf2",
```

### Godeps/_workspace/src/github.com/syndtr/goleveldb/leveldb/batch.go
```diff
@@ -15,6 +15,7 @@ import (
 	"github.com/syndtr/goleveldb/leveldb/storage"
 )
 
+// ErrBatchCorrupted records reason of batch corruption.
 type ErrBatchCorrupted struct {
 	Reason string
 }
@@ -32,6 +33,7 @@ const (
 	batchGrowRec = 3000
 )
 
+// BatchReplay wraps basic batch operations.
 type BatchReplay interface {
 	Put(key, value []byte)
 	Delete(key []byte)
@@ -68,20 +70,20 @@ func (b *Batch) grow(n int) {
 	}
 }
 
-func (b *Batch) appendRec(kt kType, key, value []byte) {
+func (b *Batch) appendRec(kt keyType, key, value []byte) {
 	n := 1 + binary.MaxVarintLen32 + len(key)
-	if kt == ktVal {
+	if kt == keyTypeVal {
 		n += binary.MaxVarintLen32 + len(value)
 	}
 	b.grow(n)
 	off := len(b.data)
 	data := b.data[:off+n]
 	data[off] = byte(kt)
-	off += 1
+	off++
 	off += binary.PutUvarint(data[off:], uint64(len(key)))
 	copy(data[off:], key)
 	off += len(key)
-	if kt == ktVal {
+	if kt == keyTypeVal {
 		off += binary.PutUvarint(data[off:], uint64(len(value)))
 		copy(data[off:], value)
 		off += len(value)
@@ -95,13 +97,13 @@ func (b *Batch) appendRec(kt kType, key, value []byte) {
 // Put appends 'put operation' of the given key/value pair to the batch.
 // It is safe to modify the contents of the argument after Put returns.
 func (b *Batch) Put(key, value []byte) {
-	b.appendRec(ktVal, key, value)
+	b.appendRec(keyTypeVal, key, value)
 }
 
 // Delete appends 'delete operation' of the given key to the batch.
 // It is safe to modify the contents of the argument after Delete returns.
 func (b *Batch) Delete(key []byte) {
-	b.appendRec(ktDel, key, nil)
+	b.appendRec(keyTypeDel, key, nil)
 }
 
 // Dump dumps batch contents. The returned slice can be loaded into the
@@ -122,11 +124,11 @@ func (b *Batch) Load(data []byte) error {
 
 // Replay replays batch contents.
 func (b *Batch) Replay(r BatchReplay) error {
-	return b.decodeRec(func(i int, kt kType, key, value []byte) error {
+	return b.decodeRec(func(i int, kt keyType, key, value []byte) error {
 		switch kt {
-		case ktVal:
+		case keyTypeVal:
 			r.Put(key, value)
-		case ktDel:
+		case keyTypeDel:
 			r.Delete(key)
 		}
 		return nil
@@ -195,18 +197,19 @@ func (b *Batch) decode(prevSeq uint64, data []byte) error {
 	return nil
 }
 
-func (b *Batch) decodeRec(f func(i int, kt kType, key, value []byte) error) error {
+func (b *Batch) decodeRec(f func(i int, kt keyType, key, value []byte) error) error {
 	off := batchHdrLen
 	for i := 0; i < b.rLen; i++ {
 		if off >= len(b.data) {
 			return newErrBatchCorrupted("invalid records length")
 		}
 
-		kt := kType(b.data[off])
-		if kt > ktVal {
+		kt := keyType(b.data[off])
+		if kt > keyTypeVal {
+			panic(kt)
 			return newErrBatchCorrupted("bad record: invalid type")
 		}
-		off += 1
+		off++
 
 		x, n := binary.Uvarint(b.data[off:])
 		off += n
@@ -216,7 +219,7 @@ func (b *Batch) decodeRec(f func(i int, kt kType, key, value []byte) error) erro
 		key := b.data[off : off+int(x)]
 		off += int(x)
 		var value []byte
-		if kt == ktVal {
+		if kt == keyTypeVal {
 			x, n := binary.Uvarint(b.data[off:])
 			off += n
 			if n <= 0 || off+int(x) > len(b.data) {
@@ -236,8 +239,8 @@ func (b *Batch) decodeRec(f func(i int, kt kType, key, value []byte) error) erro
 
 func (b *Batch) memReplay(to *memdb.DB) error {
 	var ikScratch []byte
-	return b.decodeRec(func(i int, kt kType, key, value []byte) error {
-		ikScratch = makeIkey(ikScratch, key, b.seq+uint64(i), kt)
+	return b.decodeRec(func(i int, kt keyType, key, value []byte) error {
+		ikScratch = makeInternalKey(ikScratch, key, b.seq+uint64(i), kt)
 		return to.Put(ikScratch, value)
 	})
 }
@@ -251,8 +254,8 @@ func (b *Batch) memDecodeAndReplay(prevSeq uint64, data []byte, to *memdb.DB) er
 
 func (b *Batch) revertMemReplay(to *memdb.DB) error {
 	var ikScratch []byte
-	return b.decodeRec(func(i int, kt kType, key, value []byte) error {
-		ikScratch := makeIkey(ikScratch, key, b.seq+uint64(i), kt)
+	return b.decodeRec(func(i int, kt keyType, key, value []byte) error {
+		ikScratch := makeInternalKey(ikScratch, key, b.seq+uint64(i), kt)
 		return to.Delete(ikScratch)
 	})
 }
```

### Godeps/_workspace/src/github.com/syndtr/goleveldb/leveldb/cache/cache.go
```diff
@@ -47,17 +47,21 @@ type Cacher interface {
 // so the the Release method will be called once object is released.
 type Value interface{}
 
-type CacheGetter struct {
+// NamespaceGetter provides convenient wrapper for namespace.
+type NamespaceGetter struct {
 	Cache *Cache
 	NS    uint64
 }
 
-func (g *CacheGetter) Get(key uint64, setFunc func() (size int, value Value)) *Handle {
+// Get simply calls Cache.Get() method.
+func (g *NamespaceGetter) Get(key uint64, setFunc func() (size int, value Value)) *Handle {
 	return g.Cache.Get(g.NS, key, setFunc)
 }
 
 // The hash tables implementation is based on:
-// "Dynamic-Sized Nonblocking Hash Tables", by Yujie Liu, Kunlong Zhang, and Michael Spear. ACM Symposium on Principles of Distributed Computing, Jul 2014.
+// "Dynamic-Sized Nonblocking Hash Tables", by Yujie Liu,
+// Kunlong Zhang, and Michael Spear.
+// ACM Symposium on Principles of Distributed Computing, Jul 2014.
 
 const (
 	mInitialSize           = 1 << 4
@@ -610,10 +614,12 @@ func (n *Node) unrefLocked() {
 	}
 }
 
+// Handle is a 'cache handle' of a 'cache node'.
 type Handle struct {
 	n unsafe.Pointer // *Node
 }
 
+// Value returns the value of the 'cache node'.
 func (h *Handle) Value() Value {
 	n := (*Node)(atomic.LoadPointer(&h.n))
 	if n != nil {
@@ -622,6 +628,8 @@ func (h *Handle) Value() Value {
 	return nil
 }
 
+// Release releases this 'cache handle'.
+// It is safe to call release multiple times.
 func (h *Handle) Release() {
 	nPtr := atomic.LoadPointer(&h.n)
 	if nPtr != nil && atomic.CompareAndSwapPointer(&h.n, nPtr, nil) {
```

### Godeps/_workspace/src/github.com/syndtr/goleveldb/leveldb/comparer.go
```diff
@@ -33,9 +33,9 @@ func (icmp *iComparer) Name() string {
 }
 
 func (icmp *iComparer) Compare(a, b []byte) int {
-	x := icmp.ucmp.Compare(iKey(a).ukey(), iKey(b).ukey())
+	x := icmp.ucmp.Compare(internalKey(a).ukey(), internalKey(b).ukey())
 	if x == 0 {
-		if m, n := iKey(a).num(), iKey(b).num(); m > n {
+		if m, n := internalKey(a).num(), internalKey(b).num(); m > n {
 			x = -1
 		} else if m < n {
 			x = 1
@@ -45,13 +45,13 @@ func (icmp *iComparer) Compare(a, b []byte) int {
 }
 
 func (icmp *iComparer) Separator(dst, a, b []byte) []byte {
-	ua, ub := iKey(a).ukey(), iKey(b).ukey()
+	ua, ub := internalKey(a).ukey(), internalKey(b).ukey()
 	dst = icmp.ucmp.Separator(dst, ua, ub)
 	if dst == nil {
 		return nil
 	}
 	if len(dst) < len(ua) && icmp.uCompare(ua, dst) < 0 {
-		dst = append(dst, kMaxNumBytes...)
+		dst = append(dst, keyMaxNumBytes...)
 	} else {
 		// Did not close possibilities that n maybe longer than len(ub).
 		dst = append(dst, a[len(a)-8:]...)
@@ -60,13 +60,13 @@ func (icmp *iComparer) Separator(dst, a, b []byte) []byte {
 }
 
 func (icmp *iComparer) Successor(dst, b []byte) []byte {
-	ub := iKey(b).ukey()
+	ub := internalKey(b).ukey()
 	dst = icmp.ucmp.Successor(dst, ub)
 	if dst == nil {
 		return nil
 	}
 	if len(dst) < len(ub) && icmp.uCompare(ub, dst) < 0 {
-		dst = append(dst, kMaxNumBytes...)
+		dst = append(dst, keyMaxNumBytes...)
 	} else {
 		// Did not close possibilities that n maybe longer than len(ub).
 		dst = append(dst, b[len(b)-8:]...)
```

### Godeps/_workspace/src/github.com/syndtr/goleveldb/leveldb/db.go
```diff
@@ -315,7 +315,7 @@ func recoverTable(s *session, o *opt.Options) error {
 		tw := table.NewWriter(writer, o)
 		for iter.Next() {
 			key := iter.Key()
-			if validIkey(key) {
+			if validInternalKey(key) {
 				err = tw.Append(key, iter.Value())
 				if err != nil {
 					return
@@ -380,7 +380,7 @@ func recoverTable(s *session, o *opt.Options) error {
 		// Scan the table.
 		for iter.Next() {
 			key := iter.Key()
-			_, seq, _, kerr := parseIkey(key)
+			_, seq, _, kerr := parseInternalKey(key)
 			if kerr != nil {
 				tcorruptedKey++
 				continue
@@ -472,15 +472,15 @@ func recoverTable(s *session, o *opt.Options) error {
 
 func (db *DB) recoverJournal() error {
 	// Get all journals and sort it by file number.
-	fds_, err := db.s.stor.List(storage.TypeJournal)
+	rawFds, err := db.s.stor.List(storage.TypeJournal)
 	if err != nil {
 		return err
 	}
-	sortFds(fds_)
+	sortFds(rawFds)
 
 	// Journals that will be recovered.
 	var fds []storage.FileDesc
-	for _, fd := range fds_ {
+	for _, fd := range rawFds {
 		if fd.Num >= db.s.stJournalNum || fd.Num == db.s.stPrevJournalNum {
 			fds = append(fds, fd)
 		}
@@ -633,15 +633,15 @@ func (db *DB) recoverJournal() error {
 
 func (db *DB) recoverJournalRO() error {
 	// Get all journals and sort it by file number.
-	fds_, err := db.s.stor.List(storage.TypeJournal)
+	rawFds, err := db.s.stor.List(storage.TypeJournal)
 	if err != nil {
 		return err
 	}
-	sortFds(fds_)
+	sortFds(rawFds)
 
 	// Journals that will be recovered.
 	var fds []storage.FileDesc
-	for _, fd := range fds_ {
+	for _, fd := range rawFds {
 		if fd.Num >= db.s.stJournalNum || fd.Num == db.s.stPrevJournalNum {
 			fds = append(fds, fd)
 		}
@@ -728,16 +728,16 @@ func (db *DB) recoverJournalRO() error {
 	return nil
 }
 
-func memGet(mdb *memdb.DB, ikey iKey, icmp *iComparer) (ok bool, mv []byte, err error) {
+func memGet(mdb *memdb.DB, ikey internalKey, icmp *iComparer) (ok bool, mv []byte, err error) {
 	mk, mv, err := mdb.Find(ikey)
 	if err == nil {
-		ukey, _, kt, kerr := parseIkey(mk)
+		ukey, _, kt, kerr := parseInternalKey(mk)
 		if kerr != nil {
 			// Shouldn't have had happen.
 			panic(kerr)
 		}
 		if icmp.uCompare(ukey, ikey.ukey()) == 0 {
-			if kt == ktDel {
+			if kt == keyTypeDel {
 				return true, nil, ErrNotFound
 			}
 			return true, mv, nil
@@ -750,7 +750,7 @@ func memGet(mdb *memdb.DB, ikey iKey, icmp *iComparer) (ok bool, mv []byte, err
 }
 
 func (db *DB) get(auxm *memdb.DB, auxt tFiles, key []byte, seq uint64, ro *opt.ReadOptions) (value []byte, err error) {
-	ikey := makeIkey(nil, key, seq, ktSeek)
+	ikey := makeInternalKey(nil, key, seq, keyTypeSeek)
 
 	if auxm != nil {
 		if ok, mv, me := memGet(auxm, ikey, db.s.icmp); ok {
@@ -788,7 +788,7 @@ func nilIfNotFound(err error) error {
 }
 
 func (db *DB) has(auxm *memdb.DB, auxt tFiles, key []byte, seq uint64, ro *opt.ReadOptions) (ret bool, err error) {
-	ikey := makeIkey(nil, key, seq, ktSeek)
+	ikey := makeInternalKey(nil, key, seq, keyTypeSeek)
 
 	if auxm != nil {
 		if ok, _, me := memGet(auxm, ikey, db.s.icmp); ok {
@@ -997,8 +997,8 @@ func (db *DB) SizeOf(ranges []util.Range) (Sizes, error) {
 
 	sizes := make(Sizes, 0, len(ranges))
 	for _, r := range ranges {
-		imin := makeIkey(nil, r.Start, kMaxSeq, ktSeek)
-		imax := makeIkey(nil, r.Limit, kMaxSeq, ktSeek)
+		imin := makeInternalKey(nil, r.Start, keyMaxSeq, keyTypeSeek)
+		imax := makeInternalKey(nil, r.Limit, keyMaxSeq, keyTypeSeek)
 		start, err := v.offsetOf(imin)
 		if err != nil {
 			return nil, err
@@ -1007,7 +1007,7 @@ func (db *DB) SizeOf(ranges []util.Range) (Sizes, error) {
 		if err != nil {
 			return nil, err
 		}
-		var size uint64
+		var size int64
 		if limit >= start {
 			size = limit - start
 		}
```

### Godeps/_workspace/src/github.com/syndtr/goleveldb/leveldb/db_compaction.go
```diff
@@ -452,7 +452,7 @@ func (b *tableCompactionBuilder) run(cnt *compactionTransactCounter) error {
 		}
 
 		ikey := iter.Key()
-		ukey, seq, kt, kerr := parseIkey(ikey)
+		ukey, seq, kt, kerr := parseInternalKey(ikey)
 
 		if kerr == nil {
 			shouldStop := !resumed && b.c.shouldStopBefore(ikey)
@@ -478,14 +478,14 @@ func (b *tableCompactionBuilder) run(cnt *compactionTransactCounter) error {
 
 				hasLastUkey = true
 				lastUkey = append(lastUkey[:0], ukey...)
-				lastSeq = kMaxSeq
+				lastSeq = keyMaxSeq
 			}
 
 			switch {
 			case lastSeq <= b.minSeq:
 				// Dropped because newer entry for same user key exist
 				fallthrough // (A)
-			case kt == ktDel && seq <= b.minSeq && b.c.baseLevelForKey(lastUkey):
+			case kt == keyTypeDel && seq <= b.minSeq && b.c.baseLevelForKey(lastUkey):
 				// For this user key:
 				// (1) there is no data in higher levels
 				// (2) data in lower levels will have larger seq numbers
@@ -507,7 +507,7 @@ func (b *tableCompactionBuilder) run(cnt *compactionTransactCounter) error {
 			// Don't drop corrupted keys.
 			hasLastUkey = false
 			lastUkey = lastUkey[:0]
-			lastSeq = kMaxSeq
+			lastSeq = keyMaxSeq
 			b.kerrCnt++
 		}
 
@@ -548,9 +548,7 @@ func (db *DB) tableCompaction(c *compaction, noTrivial bool) {
 		db.logf("table@move L%d@%d -> L%d", c.sourceLevel, t.fd.Num, c.sourceLevel+1)
 		rec.delTable(c.sourceLevel, t.fd.Num)
 		rec.addTableFile(c.sourceLevel+1, t)
-		db.compactionTransactFunc("table@move", func(cnt *compactionTransactCounter) (err error) {
-			return db.s.commit(rec)
-		}, nil)
+		db.compactionCommit("table-move", rec)
 		return
 	}
 
```

### Godeps/_workspace/src/github.com/syndtr/goleveldb/leveldb/db_iter.go
```diff
@@ -19,7 +19,7 @@ import (
 )
 
 var (
-	errInvalidIkey = errors.New("leveldb: Iterator: invalid internal key")
+	errInvalidInternalKey = errors.New("leveldb: Iterator: invalid internal key")
 )
 
 type memdbReleaser struct {
@@ -70,10 +70,10 @@ func (db *DB) newIterator(auxm *memDB, auxt tFiles, seq uint64, slice *util.Rang
 	if slice != nil {
 		islice = &util.Range{}
 		if slice.Start != nil {
-			islice.Start = makeIkey(nil, slice.Start, kMaxSeq, ktSeek)
+			islice.Start = makeInternalKey(nil, slice.Start, keyMaxSeq, keyTypeSeek)
 		}
 		if slice.Limit != nil {
-			islice.Limit = makeIkey(nil, slice.Limit, kMaxSeq, ktSeek)
+			islice.Limit = makeInternalKey(nil, slice.Limit, keyMaxSeq, keyTypeSeek)
 		}
 	}
 	rawIter := db.newRawIterator(auxm, auxt, islice, ro)
@@ -187,7 +187,7 @@ func (i *dbIter) Seek(key []byte) bool {
 		return false
 	}
 
-	ikey := makeIkey(nil, key, i.seq, ktSeek)
+	ikey := makeInternalKey(nil, key, i.seq, keyTypeSeek)
 	if i.iter.Seek(ikey) {
 		i.dir = dirSOI
 		return i.next()
@@ -199,15 +199,15 @@ func (i *dbIter) Seek(key []byte) bool {
 
 func (i *dbIter) next() bool {
 	for {
-		if ukey, seq, kt, kerr := parseIkey(i.iter.Key()); kerr == nil {
+		if ukey, seq, kt, kerr := parseInternalKey(i.iter.Key()); kerr == nil {
 			i.sampleSeek()
 			if seq <= i.seq {
 				switch kt {
-				case ktDel:
+				case keyTypeDel:
 					// Skip deleted key.
 					i.key = append(i.key[:0], ukey...)
 					i.dir = dirForward
-				case ktVal:
+				case keyTypeVal:
 					if i.dir == dirSOI || i.icmp.uCompare(ukey, i.key) > 0 {
 						i.key = append(i.key[:0], ukey...)
 						i.value = append(i.value[:0], i.iter.Value()...)
@@ -250,13 +250,13 @@ func (i *dbIter) prev() bool {
 	del := true
 	if i.iter.Valid() {
 		for {
-			if ukey, seq, kt, kerr := parseIkey(i.iter.Key()); kerr == nil {
+			if ukey, seq, kt, kerr := parseInternalKey(i.iter.Key()); kerr == nil {
 				i.sampleSeek()
 				if seq <= i.seq {
 					if !del && i.icmp.uCompare(ukey, i.key) < 0 {
 						return true
 					}
-					del = (kt == ktDel)
+					del = (kt == keyTypeDel)
 					if !del {
 						i.key = append(i.key[:0], ukey...)
 						i.value = append(i.value[:0], i.iter.Value()...)
@@ -292,7 +292,7 @@ func (i *dbIter) Prev() bool {
 		return i.Last()
 	case dirForward:
 		for i.iter.Prev() {
-			if ukey, _, _, kerr := parseIkey(i.iter.Key()); kerr == nil {
+			if ukey, _, _, kerr := parseInternalKey(i.iter.Key()); kerr == nil {
 				i.sampleSeek()
 				if i.icmp.uCompare(ukey, i.key) < 0 {
 					goto cont
```

### Godeps/_workspace/src/github.com/syndtr/goleveldb/leveldb/db_state.go
```diff
@@ -57,7 +57,7 @@ func (db *DB) setSeq(seq uint64) {
 	atomic.StoreUint64(&db.seq, seq)
 }
 
-func (db *DB) sampleSeek(ikey iKey) {
+func (db *DB) sampleSeek(ikey internalKey) {
 	v := db.s.version()
 	if v.sampleSeek(ikey) {
 		// Trigger table compaction.
```

### Godeps/_workspace/src/github.com/syndtr/goleveldb/leveldb/db_transaction.go
```diff
@@ -108,8 +108,8 @@ func (tr *Transaction) flush() error {
 	return nil
 }
 
-func (tr *Transaction) put(kt kType, key, value []byte) error {
-	tr.ikScratch = makeIkey(tr.ikScratch, key, tr.seq+1, kt)
+func (tr *Transaction) put(kt keyType, key, value []byte) error {
+	tr.ikScratch = makeInternalKey(tr.ikScratch, key, tr.seq+1, kt)
 	if tr.mem.Free() < len(tr.ikScratch)+len(value) {
 		if err := tr.flush(); err != nil {
 			return err
@@ -134,7 +134,7 @@ func (tr *Transaction) Put(key, value []byte, wo *opt.WriteOptions) error {
 	if tr.closed {
 		return errTransactionDone
 	}
-	return tr.put(ktVal, key, value)
+	return tr.put(keyTypeVal, key, value)
 }
 
 // Delete deletes the value for the given key.
@@ -148,7 +148,7 @@ func (tr *Transaction) Delete(key []byte, wo *opt.WriteOptions) error {
 	if tr.closed {
 		return errTransactionDone
 	}
-	return tr.put(ktDel, key, nil)
+	return tr.put(keyTypeDel, key, nil)
 }
 
 // Write apply the given batch to the transaction. The batch will be applied
@@ -167,7 +167,7 @@ func (tr *Transaction) Write(b *Batch, wo *opt.WriteOptions) error {
 	if tr.closed {
 		return errTransactionDone
 	}
-	return b.decodeRec(func(i int, kt kType, key, value []byte) error {
+	return b.decodeRec(func(i int, kt keyType, key, value []byte) error {
 		return tr.put(kt, key, value)
 	})
 }
```

### Godeps/_workspace/src/github.com/syndtr/goleveldb/leveldb/db_util.go
```diff
@@ -21,14 +21,16 @@ type Reader interface {
 	NewIterator(slice *util.Range, ro *opt.ReadOptions) iterator.Iterator
 }
 
-type Sizes []uint64
+// Sizes is list of size.
+type Sizes []int64
 
 // Sum returns sum of the sizes.
-func (p Sizes) Sum() (n uint64) {
-	for _, s := range p {
-		n += s
+func (sizes Sizes) Sum() int64 {
+	var sum int64
+	for _, size := range sizes {
+		sum += size
 	}
-	return n
+	return sum
 }
 
 // Logging.
```

### Godeps/_workspace/src/github.com/syndtr/goleveldb/leveldb/db_write.go
```diff
@@ -281,8 +281,8 @@ func (db *DB) Delete(key []byte, wo *opt.WriteOptions) error {
 func isMemOverlaps(icmp *iComparer, mem *memdb.DB, min, max []byte) bool {
 	iter := mem.NewIterator(nil)
 	defer iter.Release()
-	return (max == nil || (iter.First() && icmp.uCompare(max, iKey(iter.Key()).ukey()) >= 0)) &&
-		(min == nil || (iter.Last() && icmp.uCompare(min, iKey(iter.Key()).ukey()) <= 0))
+	return (max == nil || (iter.First() && icmp.uCompare(max, internalKey(iter.Key()).ukey()) >= 0)) &&
+		(min == nil || (iter.Last() && icmp.uCompare(min, internalKey(iter.Key()).ukey()) <= 0))
 }
 
 // CompactRange compacts the underlying DB for the given key range.
```

### Godeps/_workspace/src/github.com/syndtr/goleveldb/leveldb/filter.go
```diff
@@ -15,7 +15,7 @@ type iFilter struct {
 }
 
 func (f iFilter) Contains(filter, key []byte) bool {
-	return f.Filter.Contains(filter, iKey(key).ukey())
+	return f.Filter.Contains(filter, internalKey(key).ukey())
 }
 
 func (f iFilter) NewGenerator() filter.FilterGenerator {
@@ -27,5 +27,5 @@ type iFilterGenerator struct {
 }
 
 func (g iFilterGenerator) Add(key []byte) {
-	g.FilterGenerator.Add(iKey(key).ukey())
+	g.FilterGenerator.Add(internalKey(key).ukey())
 }
```
