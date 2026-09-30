# [?] Fixed nondeterministic hash bug

## Summary
Severity: Unknown
Chain: Stellar
Component: stellar/stellar-core
Published: 2023-03-10
Source: https://github.com/stellar/stellar-core/commit/fbf070e50568bff9a78568ebcb22aa7e517cccb0
Type: security-commit

## Details
Fixed nondeterministic hash bug

## Patch
### src/bucket/BucketIndexImpl.cpp
```diff
@@ -167,7 +167,8 @@ BucketIndexImpl<IndexT>::BucketIndexImpl(BucketManager const& bm,
                         rangeEntry.upperBound = key;
                     }
 
-                    mData.filter->insert(std::hash<stellar::LedgerKey>()(key));
+                    auto keybuf = xdr::xdr_to_opaque(key);
+                    mData.filter->insert(keybuf.data(), keybuf.size());
                 }
                 else
                 {
@@ -200,9 +201,9 @@ BucketIndexImpl<IndexT>::BucketIndexImpl(BucketManager const& bm,
 
         std::ofstream out;
         out.exceptions(std::ios::failbit | std::ios::badbit);
-        out.open(indexFilename);
+        out.open(indexFilename, std::ios_base::binary | std::ios_base::trunc);
         cereal::BinaryOutputArchive ar(out);
-        mData.save(ar);
+        ar(mData);
     }
 }
 
@@ -319,7 +320,7 @@ std::unique_ptr<BucketIndex const>
 BucketIndex::load(BucketManager const& bm,
                   std::filesystem::path const& filename, size_t bucketFileSize)
 {
-    std::ifstream in(filename);
+    std::ifstream in(filename, std::ios::binary);
     if (!in)
     {
         throw std::runtime_error(
@@ -378,8 +379,9 @@ BucketIndexImpl<IndexT>::scan(Iterator start, LedgerKey const& k) const
     // If the key is not in the bloom filter or in the lower bounded index
     // entry, return nullopt
     markBloomLookup();
+    auto keybuf = xdr::xdr_to_opaque(k);
     if ((mData.filter &&
-         !mData.filter->contains(std::hash<stellar::LedgerKey>()(k))) ||
+         !mData.filter->contains(keybuf.data(), keybuf.size())) ||
         keyIter == mData.keysToOffset.end() ||
         keyNotInIndexEntry(k, keyIter->first))
     {
```
