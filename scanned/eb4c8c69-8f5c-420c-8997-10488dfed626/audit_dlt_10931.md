# [?] Fix bug for retrieving sharding structure crash

## Summary
Severity: Unknown
Chain: Zilliqa
Component: Zilliqa/zq1
Published: 2019-01-20
Source: https://github.com/Zilliqa/zq1/commit/da1f13b0f8ffa371c91fce015a3c8e49f2b91c0b
Type: security-commit

## Details
Fix bug for retrieving sharding structure crash

## Patch
### scripts/validateBackupDB.sh
```diff
@@ -15,36 +15,17 @@
 # along with this program.  If not, see <https://www.gnu.org/licenses/>.
 
 # [MUST BE FILLED IN] User configuration settings
-aws_access_key_id=""
-aws_secret_access_key=""
-
+backupDBName=""
 
 # Validate input argument
-if [ "$#" -ne 1 ]; then
-    echo -e "\n\n\033[0;31mUsage: source ./scripts/validateBackupDB.sh backupDBName\033[0m\n"
-    return 0
-fi
-
-if [ "$aws_access_key_id" = "" ]; then
-    echo -e "\n\n\033[0;31m*ERROR* Please enter your own AWS_ACCESS_KEY_ID in validateBackupDB.sh!\033[0m\n"
-    return 0
+if [ ! -f "${backupDBName}" ]; then
+    echo -e "\n\n\033[0;31mUsage: source ./scripts/validateBackupDB.sh\033[0m\n"
+    return 1
 fi
 
-if [ "$aws_secret_access_key" = "" ]; then
-    echo -e "\n\n\033[0;31m*ERROR* Please enter your own AWS_SECRET_ACCESS_KEY in validateBackupDB.sh!\033[0m\n"
-    return 0
-fi
-
-
 # Download persistence from Amazon S3 database
-backupDBName="$1"
-export AWS_ACCESS_KEY_ID=${aws_access_key_id}
-export AWS_SECRET_ACCESS_KEY=${aws_secret_access_key}
-pip install awscli
-aws s3 cp s3://zilliqa-persistence/${backupDBName}.tar.gz ${backupDBName}.tar.gz
 rm -rf persistence
-tar xzvf ${backupDBName}.tar.gz
-echo -e "\n\033[0;32mDownload ${backupDBName}.tar.gz from Amazon S3 database successfully.\033[0m\n"
+tar xzvf ${backupDBName}
 
 
 # Configure testing environment
```

### src/libNode/Node.cpp
```diff
@@ -635,40 +635,42 @@ bool Node::StartRetrieveHistory(const SyncType syncType,
         }
       }
     }
+  }
 
-    bool bInShardStructure = false;
+  bool bInShardStructure = false;
 
-    if (bDS) {
-      m_myshardId = m_mediator.m_ds->m_shards.size();
-    } else {
-      for (unsigned int i = 0;
-           i < m_mediator.m_ds->m_shards.size() && !bInShardStructure; ++i) {
-        for (const auto& shardNode : m_mediator.m_ds->m_shards.at(i)) {
-          if (get<SHARD_NODE_PUBKEY>(shardNode) ==
-              m_mediator.m_selfKey.second) {
-            SetMyshardId(i);
-            bInShardStructure = true;
-            break;
-          }
+  if (bDS) {
+    m_myshardId = m_mediator.m_ds->m_shards.size();
+  } else {
+    for (unsigned int i = 0;
+         i < m_mediator.m_ds->m_shards.size() && !bInShardStructure; ++i) {
+      for (const auto& shardNode : m_mediator.m_ds->m_shards.at(i)) {
+        if (get<SHARD_NODE_PUBKEY>(shardNode) == m_mediator.m_selfKey.second) {
+          SetMyshardId(i);
+          LOG_GENERAL(
+              INFO, "This node belongs to sharding structure #" << m_myshardId);
+          bInShardStructure = true;
+          break;
         }
       }
     }
+  }
 
-    if (LOOKUP_NODE_MODE) {
-      m_mediator.m_lookup->ProcessEntireShardingStructure();
-    } else {
-      LoadShardingStructure(true);
-      m_mediator.m_ds->ProcessShardingStructure(
-          m_mediator.m_ds->m_shards, m_mediator.m_ds->m_publicKeyToshardIdMap,
-          m_mediator.m_ds->m_mapNodeReputation);
-    }
+  if (LOOKUP_NODE_MODE) {
+    m_mediator.m_lookup->ProcessEntireShardingStructure();
+  } else {
+    LoadShardingStructure(true);
+    m_mediator.m_ds->ProcessShardingStructure(
+        m_mediator.m_ds->m_shards, m_mediator.m_ds->m_publicKeyToshardIdMap,
+        m_mediator.m_ds->m_mapNodeReputation);
+  }
 
-    if (REJOIN_NODE_NOT_IN_NETWORK && !LOOKUP_NODE_MODE && !bDS &&
-        !bInShardStructure) {
-      LOG_GENERAL(WARNING,
-                  "Node is not in network, apply re-join process instead");
-      return false;
-    }
+  if (REJOIN_NODE_NOT_IN_NETWORK && !LOOKUP_NODE_MODE && !bDS &&
+      !bInShardStructure) {
+    LOG_GENERAL(WARNING,
+                "Node " << m_mediator.m_selfKey.second
+                        << " is not in network, apply re-join process instead");
+    return false;
   }
 
   m_mediator.m_consensusID =
```

### tests/Zilliqa/test_zilliqa_local.py
```diff
@@ -304,7 +304,7 @@ def run_start_validateBackupDB():
 	shutil.copyfile('constants_local.xml', LOCAL_RUN_FOLDER + testfolders_list[0] + '/constants.xml')
 	shutil.copyfile('dsnodes.xml', LOCAL_RUN_FOLDER + testfolders_list[0] + '/dsnodes.xml')
 	shutil.copyfile('config_normal.xml', LOCAL_RUN_FOLDER + testfolders_list[0] + '/config.xml')
-	os.system('cd ' + LOCAL_RUN_FOLDER + testfolders_list[0] + '; echo \"' + keypair[0] + ' ' + keypair[1] + '\" > mykey.txt' + '; ulimit -n 65535; ulimit -Sc unlimited; ulimit -Hc unlimited; $(pwd)/zilliqa ' + keypair[1] + ' ' + keypair[0] + ' ' + '127.0.0.1' +' ' + str(NODE_LISTEN_PORT + 0) + ' 1 5 1 > ./error_log_zilliqa 2>&1 &')
+	os.system('cd ' + LOCAL_RUN_FOLDER + testfolders_list[0] + '; echo \"' + keypair[0] + ' ' + keypair[1] + '\" > mykey.txt' + '; ulimit -n 65535; ulimit -Sc unlimited; ulimit -Hc unlimited; $(pwd)/zilliqa ' + ' --privk ' + keypair[1] + ' --pubk ' + keypair[0] + ' --address ' + '127.0.0.1' + ' --port ' + str(NODE_LISTEN_PORT + 0) + ' --loadconfig 1 --synctype 5 --recovery 1 > ./error_log_zilliqa 2>&1 &')
 
 def run_connect(numnodes):
 	testfolders_list = get_immediate_subdirectories(LOCAL_RUN_FOLDER)
```
