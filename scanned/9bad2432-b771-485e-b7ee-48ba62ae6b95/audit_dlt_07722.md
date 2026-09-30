# [?] Fix crash with unsupported fork name and add YOLOv2 compatibility (for evm tool) (#1584)

## Summary
Severity: Unknown
Chain: Ethereum
Component: besu-eth/besu
Published: 2020-11-20
Source: https://github.com/besu-eth/besu/commit/1c7636487277d7b737cc94839ec24668bb1849b7
Type: security-commit

## Details
Fix crash with unsupported fork name and add YOLOv2 compatibility (for evm tool) (#1584)

Signed-off-by: Karim TAAM <karim.t2am@gmail.com>

## Patch
### CHANGELOG.md
```diff
@@ -9,6 +9,7 @@
 ### Bug Fixes
 
 * Ibft2 will discard any received messages targetting a chain height <= current head - this resolves some corner cases in system correctness directly following block import. [#1575](https://github.com/hyperledger/besu/pull/1575)
+* EvmTool now throws `UnsupportedForkException` when there is an unknown fork and is YOLOv2 compatible [\#1584](https://github.com/hyperledger/besu/pull/1584)
 
 ## 20.10.1
 
```

### ethereum/evmtool/build.gradle
```diff
@@ -54,6 +54,10 @@ dependencies {
   implementation 'org.apache.logging.log4j:log4j-core'
 
   annotationProcessor 'com.google.dagger:dagger-compiler'
+
+  testImplementation 'junit:junit'
+  testImplementation 'org.assertj:assertj-core'
+  testImplementation 'org.mockito:mockito-core'
 }
 
 mainClassName = 'org.hyperledger.besu.evmtool.EvmTool'
```

### ethereum/evmtool/src/main/java/org/hyperledger/besu/evmtool/StateTestSubCommand.java
```diff
@@ -28,6 +28,7 @@
 import org.hyperledger.besu.ethereum.core.WorldState;
 import org.hyperledger.besu.ethereum.core.WorldUpdater;
 import org.hyperledger.besu.ethereum.mainnet.MainnetTransactionProcessor;
+import org.hyperledger.besu.ethereum.mainnet.ProtocolSchedule;
 import org.hyperledger.besu.ethereum.mainnet.TransactionValidationParams;
 import org.hyperledger.besu.ethereum.processing.TransactionProcessingResult;
 import org.hyperledger.besu.ethereum.referencetests.GeneralStateTestCaseEipSpec;
@@ -39,6 +40,7 @@
 import org.hyperledger.besu.ethereum.vm.OperationTracer;
 import org.hyperledger.besu.ethereum.vm.StandardJsonTracer;
 import org.hyperledger.besu.ethereum.worldstate.DefaultMutableWorldState;
+import org.hyperledger.besu.evmtool.exception.UnsupportedForkException;
 
 import java.io.BufferedReader;
 import java.io.File;
@@ -90,6 +92,12 @@ public class StateTestSubCommand implements Runnable {
 
   private final ObjectMapper objectMapper = new ObjectMapper();
 
+  public StateTestSubCommand() {}
+
+  public StateTestSubCommand(final EvmToolCommand parentCommand) {
+    this.parentCommand = parentCommand;
+  }
+
   @Override
   public void run() {
     final ObjectMapper objectMapper = new ObjectMapper();
@@ -169,11 +177,14 @@ private void traceTestSpecs(final String test, final List<GeneralStateTestCaseEi
         return;
       }
 
+      final String forkName = fork == null ? spec.getFork() : fork;
+      final ProtocolSchedule protocolSchedule = referenceTestProtocolSchedules.getByName(forkName);
+      if (protocolSchedule == null) {
+        throw new UnsupportedForkException(forkName);
+      }
+
       final MainnetTransactionProcessor processor =
-          referenceTestProtocolSchedules
-              .getByName(fork == null ? spec.getFork() : fork)
-              .getByBlockNumber(0)
-              .getTransactionProcessor();
+          protocolSchedule.getByBlockNumber(0).getTransactionProcessor();
       final WorldUpdater worldStateUpdater = worldState.updater();
       final ReferenceTestBlockchain blockchain =
           new ReferenceTestBlockchain(blockHeader.getNumber());
```

### ethereum/evmtool/src/main/java/org/hyperledger/besu/evmtool/exception/UnsupportedForkException.java
```diff
@@ -0,0 +1,23 @@
+/*
+ * Copyright 2018 ConsenSys AG.
+ *
+ * Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
+ * the License. You may obtain a copy of the License at
+ *
+ * http://www.apache.org/licenses/LICENSE-2.0
+ *
+ * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
+ * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
+ * specific language governing permissions and limitations under the License.
+ *
+ * SPDX-License-Identifier: Apache-2.0
+ *
+ */
+package org.hyperledger.besu.evmtool.exception;
+
+public class UnsupportedForkException extends RuntimeException {
+
+  public UnsupportedForkException(final String forkName) {
+    super(String.format("Fork '%s' not supported", forkName));
+  }
+}
```

### ethereum/evmtool/src/test/java/org/hyperledger/besu/evmtool/StateTestSubCommandTest.java
```diff
@@ -0,0 +1,44 @@
+/*
+ * Copyright ConsenSys AG.
+ *
+ * Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
+ * the License. You may obtain a copy of the License at
+ *
+ * http://www.apache.org/licenses/LICENSE-2.0
+ *
+ * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
+ * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
+ * specific language governing permissions and limitations under the License.
+ *
+ * SPDX-License-Identifier: Apache-2.0
+ */
+package org.hyperledger.besu.evmtool;
+
+import static org.assertj.core.api.Assertions.assertThatThrownBy;
+
+import org.hyperledger.besu.evmtool.exception.UnsupportedForkException;
+
+import org.junit.Test;
+import picocli.CommandLine;
+
+public class StateTestSubCommandTest {
+
+  @Test
+  public void shouldDetectUnsupportedFork() {
+    final StateTestSubCommand stateTestSubCommand = new StateTestSubCommand(new EvmToolCommand());
+    final CommandLine cmd = new CommandLine(stateTestSubCommand);
+    cmd.parseArgs(
+        StateTestSubCommandTest.class.getResource("unsupported-fork-state-test.json").getPath());
+    assertThatThrownBy(stateTestSubCommand::run)
+        .hasMessageContaining("Fork 'UnknownFork' not supported")
+        .isInstanceOf(UnsupportedForkException.class);
+  }
+
+  @Test
+  public void shouldWorkWithValidStateTest() {
+    final StateTestSubCommand stateTestSubCommand = new StateTestSubCommand(new EvmToolCommand());
+    final CommandLine cmd = new CommandLine(stateTestSubCommand);
+    cmd.parseArgs(StateTestSubCommandTest.class.getResource("valid-state-test.json").getPath());
+    stateTestSubCommand.run();
+  }
+}
```

### ethereum/evmtool/src/test/resources/org/hyperledger/besu/evmtool/unsupported-fork-state-test.json
```diff
@@ -0,0 +1,85 @@
+{
+  "callcallcodecall_010_SuicideEnd" : {
+    "_info" : {
+      "comment" : "",
+      "filling-rpc-server" : "Geth-1.9.6-unstable-63b18027-20190920",
+      "filling-tool-version" : "retesteth-0.0.1+commit.0ae18aef.Linux.g++",
+      "lllcversion" : "Version: 0.5.12-develop.2019.9.13+commit.2d601a4f.Linux.g++",
+      "source" : "src/GeneralStateTestsFiller/stCallDelegateCodesCallCodeHomestead/callcallcodecall_010_SuicideEndFiller.json",
+      "sourceHash" : "6d86c07af29329a8944aa6953d4271f5adfe2f9b0554294f2d7a54827f409569"
+    },
+    "env" : {
+      "currentCoinbase" : "0x2adc25665018aa1fe0e6bc666dac8fc2697ff9ba",
+      "currentDifficulty" : "0x020000",
+      "currentGasLimit" : "0x01c9c380",
+      "currentNumber" : "0x01",
+      "currentTimestamp" : "0x03e8",
+      "previousHash" : "0x5e20a0453cecd065ea59c37ac63e079ee08998b6045136a8ce6635c7912ec0b6"
+    },
+    "post" : {
+      "UnknownFork" : [
+        {
+          "indexes" : {
+            "data" : 0,
+            "gas" : 0,
+            "value" : 0
+          },
+          "hash" : "0x0ff25ed40ebe791efa00daa61bbb998db905b529fa0f8f2afb9e1aa69b63442c",
+          "logs" : "0x1dcc4de8dec75d7aab85b567b6ccd41ad312451b948a7413f0a142fd40d49347"
+        }
+      ]
+    },
+    "pre" : {
+      "0x1000000000000000000000000000000000000000" : {
+        "balance" : "0x0de0b6b3a7640000",
+        "code" : "0x60406000604060006000731000000000000000000000000000000000000001620249f0f260005500",
+        "nonce" : "0x00",
+        "storage" : {
+        }
+      },
+      "0x1000000000000000000000000000000000000001" : {
+        "balance" : "0x02540be400",
+        "code" : "0x6040600060406000731000000000000000000000000000000000000002620186a0f460015500",
+        "nonce" : "0x00",
+        "storage" : {
+        }
+      },
+      "0x1000000000000000000000000000000000000002" : {
+        "balance" : "0x02540be400",
+        "code" : "0x6040600060406000600073100000000000000000000000000000000000000361c350f2600255731000000000000000000000000000000000000001ff00",
+        "nonce" : "0x00",
+        "storage" : {
+        }
+      },
+      "0x1000000000000000000000000000000000000003" : {
+        "balance" : "0x02540be400",
+        "code" : "0x600160035500",
+        "nonce" : "0x00",
+        "storage" : {
+        }
+      },
+      "0xa94f5374fce5edbc8e2a8697c15331677e6ebf0b" : {
+        "balance" : "0x0de0b6b3a7640000",
+        "code" : "0x",
+        "nonce" : "0x00",
+        "storage" : {
+        }
+      }
+    },
+    "transaction" : {
+      "data" : [
+        "0x"
+      ],
+      "gasLimit" : [
+        "0x2dc6c0"
+      ],
+      "gasPrice" : "0x01",
+      "nonce" : "0x00",
+      "secretKey" : "0x45a915e4d060149eb4365960e6a7a45f334393093061116b197e3240065ff2d8",
+      "to" : "0x1000000000000000000000000000000000000000",
+      "value" : [
+        "0x00"
+      ]
+    }
+  }
+}
\ No newline at end of file
```

### ethereum/evmtool/src/test/resources/org/hyperledger/besu/evmtool/valid-state-test.json
```diff
@@ -0,0 +1,85 @@
+{
+  "callcallcodecall_010_SuicideEnd" : {
+    "_info" : {
+      "comment" : "",
+      "filling-rpc-server" : "Geth-1.9.6-unstable-63b18027-20190920",
+      "filling-tool-version" : "retesteth-0.0.1+commit.0ae18aef.Linux.g++",
+      "lllcversion" : "Version: 0.5.12-develop.2019.9.13+commit.2d601a4f.Linux.g++",
+      "source" : "src/GeneralStateTestsFiller/stCallDelegateCodesCallCodeHomestead/callcallcodecall_010_SuicideEndFiller.json",
+      "sourceHash" : "6d86c07af29329a8944aa6953d4271f5adfe2f9b0554294f2d7a54827f409569"
+    },
+    "env" : {
+      "currentCoinbase" : "0x2adc25665018aa1fe0e6bc666dac8fc2697ff9ba",
+      "currentDifficulty" : "0x020000",
+      "currentGasLimit" : "0x01c9c380",
+      "currentNumber" : "0x01",
+      "currentTimestamp" : "0x03e8",
+      "previousHash" : "0x5e20a0453cecd065ea59c37ac63e079ee08998b6045136a8ce6635c7912ec0b6"
+    },
+    "post" : {
+      "Istanbul" : [
+        {
+          "indexes" : {
+            "data" : 0,
+            "gas" : 0,
+            "value" : 0
+          },
+          "hash" : "0x0ff25ed40ebe791efa00daa61bbb998db905b529fa0f8f2afb9e1aa69b63442c",
+          "logs" : "0x1dcc4de8dec75d7aab85b567b6ccd41ad312451b948a7413f0a142fd40d49347"
+        }
+      ]
+    },
+    "pre" : {
+      "0x1000000000000000000000000000000000000000" : {
+        "balance" : "0x0de0b6b3a7640000",
+        "code" : "0x60406000604060006000731000000000000000000000000000000000000001620249f0f260005500",
+        "nonce" : "0x00",
+        "storage" : {
+        }
+      },
+      "0x1000000000000000000000000000000000000001" : {
+        "balance" : "0x02540be400",
+        "code" : "0x6040600060406000731000000000000000000000000000000000000002620186a0f460015500",
+        "nonce" : "0x00",
+        "storage" : {
+        }
+      },
+      "0x1000000000000000000000000000000000000002" : {
+        "balance" : "0x02540be400",
+        "code" : "0x6040600060406000600073100000000000000000000000000000000000000361c350f2600255731000000000000000000000000000000000000001ff00",
+        "nonce" : "0x00",
+        "storage" : {
+        }
+      },
+      "0x1000000000000000000000000000000000000003" : {
+        "balance" : "0x02540be400",
+        "code" : "0x600160035500",
+        "nonce" : "0x00",
+        "storage" : {
+        }
+      },
+      "0xa94f5374fce5edbc8e2a8697c15331677e6ebf0b" : {
+        "balance" : "0x0de0b6b3a7640000",
+        "code" : "0x",
+        "nonce" : "0x00",
+        "storage" : {
+        }
+      }
+    },
+    "transaction" : {
+      "data" : [
+        "0x"
+      ],
+      "gasLimit" : [
+        "0x2dc6c0"
+      ],
+      "gasPrice" : "0x01",
+      "nonce" : "0x00",
+      "secretKey" : "0x45a915e4d060149eb4365960e6a7a45f334393093061116b197e3240065ff2d8",
+      "to" : "0x1000000000000000000000000000000000000000",
+      "value" : [
+        "0x00"
+      ]
+    }
+  }
+}
\ No newline at end of file
```

### ethereum/referencetests/src/main/java/org/hyperledger/besu/ethereum/referencetests/ReferenceTestProtocolSchedules.java
```diff
@@ -64,6 +64,7 @@ public static ReferenceTestProtocolSchedules create() {
     builder.put("MuirGlacier", createSchedule(new StubGenesisConfigOptions().muirGlacierBlock(0)));
     if (ExperimentalEIPs.berlinEnabled) {
       builder.put("Berlin", createSchedule(new StubGenesisConfigOptions().berlinBlock(0)));
+      builder.put("YOLOv2", createSchedule(new StubGenesisConfigOptions().berlinBlock(0)));
     }
     return new ReferenceTestProtocolSchedules(builder.build());
   }
```
