# [?] fix: resolve potential deadlock

## Summary
Severity: Unknown
Chain: Dash
Component: dashpay/dash
Published: 2025-10-28
Source: https://github.com/dashpay/dash/commit/0bc28c314cfffb68391d2128a68a22ee4648eb14
Type: security-commit

## Details
fix: resolve potential deadlock

## Patch
### src/governance/governance.cpp
```diff
@@ -981,7 +981,12 @@ bool CGovernanceManager::ProcessVote(CNode* pfrom, const CGovernanceVote& vote,
         return false;
     }
 
-    bool fOk = govobj.ProcessVote(m_mn_metaman, *this, Assert(m_dmnman)->GetListAtChainTip(), vote, exception) && cmapVoteToObject.Insert(nHashVote, &govobj);
+    bool fOk = govobj.ProcessVote(m_mn_metaman, *this, Assert(m_dmnman)->GetListAtChainTip(), vote, exception);
+    if (fOk) {
+        fOk = cmapVoteToObject.Insert(nHashVote, &govobj);
+    } else if (exception.GetType() == GOVERNANCE_EXCEPTION_PERMANENT_ERROR && exception.GetNodePenalty() == 20) {
+        cmapInvalidVotes.Insert(nHashVote, vote);
+    }
     LEAVE_CRITICAL_SECTION(cs_store);
     return fOk;
 }
@@ -1086,12 +1091,6 @@ void CGovernanceManager::RequestGovernanceObject(CNode* pfrom, const uint256& nH
     connman.PushMessage(pfrom, msgMaker.Make(NetMsgType::MNGOVERNANCESYNC, nHash, filter));
 }
 
-void CGovernanceManager::AddInvalidVote(const CGovernanceVote& vote)
-{
-    LOCK(cs_store);
-    cmapInvalidVotes.Insert(vote.GetHash(), vote);
-}
-
 int CGovernanceManager::RequestGovernanceObjectVotes(CNode& peer, CConnman& connman, const PeerManager& peerman) const
 {
     const std::vector<CNode*> vNodeCopy{&peer};
```

### src/governance/governance.h
```diff
@@ -296,8 +296,6 @@ class CGovernanceManager : public GovernanceStore, public GovernanceSignerParent
 
     // CGovernanceObject
     bool AreRateChecksEnabled() const { return fRateChecksEnabled; }
-    void AddInvalidVote(const CGovernanceVote& vote)
-        EXCLUSIVE_LOCKS_REQUIRED(!cs_store);
 
     // Getters/Setters
     int GetCachedBlockHeight() const override { return nCachedBlockHeight; }
```

### src/governance/object.cpp
```diff
@@ -144,7 +144,6 @@ bool CGovernanceObject::ProcessVote(CMasternodeMetaMan& mn_metaman, CGovernanceM
             __func__, vote.GetMasternodeOutpoint().ToStringShort(), GetHash().ToString(), vote.GetHash().ToString())};
         LogPrintf("%s\n", msg);
         exception = CGovernanceException(msg, GOVERNANCE_EXCEPTION_PERMANENT_ERROR, 20);
-        govman.AddInvalidVote(vote);
         return false;
     }
 
```
