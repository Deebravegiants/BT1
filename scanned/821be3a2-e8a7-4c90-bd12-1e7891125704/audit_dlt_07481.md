# [?] Merge #8408: Prevent fingerprinting, disk-DoS with compact blocks

## Summary
Severity: Unknown
Chain: Dogecoin
Component: dogecoin/dogecoin
Published: 2016-07-29
Source: https://github.com/dogecoin/dogecoin/commit/842bf8d2c5af86bc94e586d8acd5e5ab7c59ddc0
Type: security-commit

## Details
Merge #8408: Prevent fingerprinting, disk-DoS with compact blocks

1d06e49 Ignore CMPCTBLOCK messages for pruned blocks (Suhas Daftuar)
1de2a46 Ignore GETBLOCKTXN requests for unknown blocks (Suhas Daftuar)

## Patch
### src/main.cpp
```diff
@@ -5343,7 +5343,6 @@ bool static ProcessMessage(CNode* pfrom, string strCommand, CDataStream& vRecv,
 
         BlockMap::iterator it = mapBlockIndex.find(req.blockhash);
         if (it == mapBlockIndex.end() || !(it->second->nStatus & BLOCK_HAVE_DATA)) {
-            Misbehaving(pfrom->GetId(), 100);
             LogPrintf("Peer %d sent us a getblocktxn for a block we don't have", pfrom->id);
             return true;
         }
@@ -5627,8 +5626,8 @@ bool static ProcessMessage(CNode* pfrom, string strCommand, CDataStream& vRecv,
                 std::vector<CInv> vInv(1);
                 vInv[0] = CInv(MSG_BLOCK, cmpctblock.header.GetHash());
                 pfrom->PushMessage(NetMsgType::GETDATA, vInv);
-                return true;
             }
+            return true;
         }
 
         // If we're not close to tip yet, give up and let parallel block fetch work its magic
```
