# [?] Limit how many reads we defer to avoid overflowing the cache

## Summary
Severity: Unknown
Chain: XRP
Component: XRPLF/rippled
Published: 2014-03-07
Source: https://github.com/XRPLF/rippled/commit/b4593a274d7295e58dc3c4dc4ae0d94c2d31d343
Type: security-commit

## Details
Limit how many reads we defer to avoid overflowing the cache

## Patch
### src/ripple_app/shamap/SHAMapSync.cpp
```diff
@@ -132,14 +132,18 @@ void SHAMap::getMissingNodes (std::vector<SHAMapNode>& nodeIDs, std::vector<uint
         return;
     }
 
+    int const maxDefer = getApp().getNodeStore().getDesiredAsyncReadCount ();
+
     // Track the missing hashes we have found so far
     std::set <uint256> missingHashes;
 
+
     while (1)
     {
+        std::vector <std::pair <SHAMapNode, uint256>> deferredReads;
+        deferredReads.reserve (maxDefer + 16);
 
         std::stack <GMNEntry> stack;
-        int deferCount = 0;
 
         // Traverse the map without blocking
 
@@ -179,7 +183,7 @@ void SHAMap::getMissingNodes (std::vector<SHAMapNode>& nodeIDs, std::vector<uint
                             else
                             {
                                 // read is deferred
-                                ++deferCount;
+                                deferredReads.emplace_back (childID, childHash);
                             }
 
                             fullBelow = false; // This node is not known full below
@@ -220,13 +224,30 @@ void SHAMap::getMissingNodes (std::vector<SHAMapNode>& nodeIDs, std::vector<uint
             }
 
         }
-        while (node != NULL);
+        while ((node != NULL) && (deferredReads.size () <= maxDefer));
 
         // If we didn't defer any reads, we're done
-        if (deferCount == 0)
+        if (deferredReads.empty ())
             break;
 
         getApp().getNodeStore().waitReads();
+
+        // Process all deferred reads
+        for (auto const& node : deferredReads)
+        {
+            auto const& nodeID = node.first;
+            auto const& nodeHash = node.second;
+            SHAMapNode *nodePtr = getNodePointerNT (nodeID, nodeHash, filter);
+            if (!nodePtr && missingHashes.insert (nodeHash).second)
+            {
+                nodeIDs.push_back (nodeID);
+                hashes.push_back (nodeHash);
+
+                if (--max <= 0)
+                    return;
+            }
+        }
+
     }
 
     if (nodeIDs.empty ())
```

### src/ripple_core/nodestore/api/Database.h
```diff
@@ -79,6 +79,11 @@ class Database
     */
     virtual void waitReads () = 0;
 
+    /** Get the maximum number of async reads the node store prefers.
+        @return The number of async reads preferred.
+    */
+    virtual int getDesiredAsyncReadCount () = 0;
+
     /** Store the object.
 
         The caller's Blob parameter is overwritten.
```

### src/ripple_core/nodestore/impl/DatabaseImp.h
```diff
@@ -126,6 +126,12 @@ class DatabaseImp
 
     }
 
+    int getDesiredAsyncReadCount ()
+    {
+        // We prefer a client not fill our cache
+        return m_cache.getTargetSize() / 4;
+    }
+
     NodeObject::Ptr fetch (uint256 const& hash)
     {
         // See if the object already exists in the cache
```
