# [?] [master] ZIL-5127: fix assertion/crash due to OTel protobuf  (#3501)

## Summary
Severity: Unknown
Chain: Zilliqa
Component: Zilliqa/zq1
Published: 2023-03-10
Source: https://github.com/Zilliqa/zq1/commit/7101dfcc5e0170bf8b70dc3becbb699e247f1651
Type: security-commit

## Details
[master] ZIL-5127: fix assertion/crash due to OTel protobuf  (#3501)

* Simplify some #includes.
* Patch OTel vcpkg port to create its proto library as a shared library.

## Patch
### src/libDirectoryService/Coinbase.cpp
```diff
@@ -29,7 +29,7 @@
 using namespace std;
 using namespace boost::multiprecision;
 
-template <class Container>
+template <typename Container>
 bool DirectoryService::SaveCoinbaseCore(const vector<bool>& b1,
                                         const vector<bool>& b2,
                                         const Container& shard,
```

### src/libDirectoryService/DirectoryService.h
```diff
@@ -18,24 +18,13 @@
 #ifndef ZILLIQA_SRC_LIBDIRECTORYSERVICE_DIRECTORYSERVICE_H_
 #define ZILLIQA_SRC_LIBDIRECTORYSERVICE_DIRECTORYSERVICE_H_
 
-#include <array>
-#include <condition_variable>
-#include <map>
-#include <set>
-#include <shared_mutex>
-
-#include <Schnorr.h>
-#include "common/Constants.h"
 #include "libBlockchain/Block.h"
-#include "libBlockchain/BlockHashSet.h"
 #include "libConsensus/Consensus.h"
 #include "libData/MiningData/DSPowSolution.h"
 #include "libLookup/Synchronizer.h"
 #include "libNetwork/DataSender.h"
 #include "libNetwork/Executable.h"
-#include "libNetwork/P2PComm.h"
 #include "libNetwork/ShardStruct.h"
-#include "libPersistence/BlockStorage.h"
 #include "libUtils/TimeUtils.h"
 
 class Mediator;
@@ -646,7 +635,7 @@ class DirectoryService : public Executable {
   void InitCoinbase();
   void StoreCoinbaseInDiagnosticDB(const DiagnosticDataCoinbase& entry);
 
-  template <class Container>
+  template <typename Container>
   bool SaveCoinbaseCore(const std::vector<bool>& b1,
                         const std::vector<bool>& b2, const Container& shard,
                         const int32_t& shard_id, const uint64_t& epochNum);
```

### src/libNode/DSBlockProcessing.cpp
```diff
@@ -15,11 +15,6 @@
  * along with this program.  If not, see <https://www.gnu.org/licenses/>.
  */
 
-#include <array>
-#include <chrono>
-#include <functional>
-#include <thread>
-
 #include "Node.h"
 #include "common/Constants.h"
 #include "common/Messages.h"
@@ -32,6 +27,7 @@
 #include "libMessage/Messenger.h"
 #include "libNetwork/Blacklist.h"
 #include "libNetwork/Guard.h"
+#include "libNetwork/P2PComm.h"
 #include "libPOW/pow.h"
 #include "libUtils/BitVector.h"
 #include "libUtils/DataConversion.h"
```

### src/libNode/MicroBlockPostProcessing.cpp
```diff
@@ -38,7 +38,6 @@
 
 using namespace std;
 using namespace boost::multiprecision;
-using namespace boost::multi_index;
 
 bool Node::ComposeMicroBlockMessageForSender(zbytes& microblock_message) const {
   if (LOOKUP_NODE_MODE) {
```

### src/libNode/MicroBlockPreProcessing.cpp
```diff
@@ -27,6 +27,7 @@
 #include "libData/AccountStore/AccountStore.h"
 #include "libMediator/Mediator.h"
 #include "libMessage/Messenger.h"
+#include "libNetwork/P2PComm.h"
 #include "libPOW/pow.h"
 #include "libUtils/BitVector.h"
 #include "libUtils/DataConversion.h"
@@ -39,7 +40,6 @@
 
 using namespace std;
 using namespace boost::multiprecision;
-using namespace boost::multi_index;
 
 bool Node::ComposeMicroBlock(const uint64_t& microblock_gas_limit) {
   if (LOOKUP_NODE_MODE) {
```

### src/libNode/Node.cpp
```diff
@@ -16,18 +16,12 @@
  */
 
 #include <arpa/inet.h>
-#include <array>
-#include <chrono>
-#include <functional>
-#include <thread>
-#include <tuple>
 
 #include <boost/algorithm/string.hpp>
 #include <boost/filesystem.hpp>
 #include <boost/property_tree/ptree.hpp>
 #include <boost/property_tree/xml_parser.hpp>
 
-#include <Schnorr.h>
 #include "Node.h"
 #include "common/Constants.h"
 #include "common/Messages.h"
@@ -41,6 +35,7 @@
 #include "libMetrics/Api.h"
 #include "libNetwork/Blacklist.h"
 #include "libNetwork/Guard.h"
+#include "libNetwork/P2PComm.h"
 #include "libPOW/pow.h"
 #include "libPersistence/Retriever.h"
 #include "libPythonRunner/PythonRunner.h"
@@ -54,7 +49,6 @@
 
 using namespace std;
 using namespace boost::multiprecision;
-using namespace boost::multi_index;
 
 const unsigned int MIN_CLUSTER_SIZE = 2;
 const unsigned int MIN_CHILD_CLUSTER_SIZE = 2;
```

### src/libNode/PoWProcessing.cpp
```diff
@@ -31,6 +31,7 @@
 #include "libMediator/Mediator.h"
 #include "libMessage/Messenger.h"
 #include "libNetwork/Guard.h"
+#include "libNetwork/P2PComm.h"
 #include "libPOW/pow.h"
 #include "libUtils/DataConversion.h"
 #include "libUtils/DetachedFunction.h"
```

### vcpkg-registry/ports/opentelemetry-cpp/portfile.cmake
```diff
@@ -10,6 +10,7 @@ vcpkg_from_github(
     HEAD_REF main
     PATCHES
         mac-fix.patch
+        proto-shared.patch
 )
 
 vcpkg_check_features(OUT_FEATURE_OPTIONS FEATURE_OPTIONS
@@ -49,6 +50,7 @@ vcpkg_cmake_configure(
         -DWITH_LOGS_PREVIEW=ON
         -DWITH_STL=ON
         -DWITH_OTLP_GRPC=ON
+        -DBUILD_SHARED_LIBS=OFF
         ${FEATURE_OPTIONS}
 )
 
```

### vcpkg-registry/ports/opentelemetry-cpp/proto-shared.patch
```diff
@@ -0,0 +1,37 @@
+diff --git a/cmake/opentelemetry-proto.cmake b/cmake/opentelemetry-proto.cmake
+index a21c0f1..0181de3 100644
+--- a/cmake/opentelemetry-proto.cmake
++++ b/cmake/opentelemetry-proto.cmake
+@@ -226,9 +226,15 @@ endif()
+ 
+ include_directories("${GENERATED_PROTOBUF_PATH}")
+ 
++if(BUILD_SHARED_LIBS)
++  set(OPENTELEMETRY_PROTO_LIBRARY_TYPE SHARED)
++else()
++  set(OPENTELEMETRY_PROTO_LIBRARY_TYPE STATIC)
++endif()
++
+ if(WITH_OTLP_GRPC)
+   add_library(
+-    opentelemetry_proto STATIC
++    opentelemetry_proto ${OPENTELEMETRY_PROTO_LIBRARY_TYPE}
+     ${COMMON_PB_CPP_FILE}
+     ${RESOURCE_PB_CPP_FILE}
+     ${TRACE_PB_CPP_FILE}
+@@ -242,7 +248,7 @@ if(WITH_OTLP_GRPC)
+     ${METRICS_SERVICE_GRPC_PB_CPP_FILE})
+ else()
+   add_library(
+-    opentelemetry_proto STATIC
++    opentelemetry_proto ${OPENTELEMETRY_PROTO_LIBRARY_TYPE}
+     ${COMMON_PB_CPP_FILE}
+     ${RESOURCE_PB_CPP_FILE}
+     ${TRACE_PB_CPP_FILE}
+@@ -282,4 +288,5 @@ endif()
+ 
+ if(BUILD_SHARED_LIBS)
+   set_property(TARGET opentelemetry_proto PROPERTY POSITION_INDEPENDENT_CODE ON)
++  target_link_libraries(opentelemetry_proto PRIVATE gRPC::grpc++)
+ endif()
+
```
