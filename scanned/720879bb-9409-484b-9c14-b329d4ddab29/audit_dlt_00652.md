# [?] Merge bitcoin-core/gui#944: Fix out-of-bounds read in RPCParseCommandLine on empty command

## Summary
Severity: Unknown
Chain: Bitcoin
Component: bitcoin/bitcoin
Published: 2026-08-20
Source: https://github.com/bitcoin/bitcoin/commit/87b8a4ee506e3328decbfb304344774797b104f6
Type: security-commit

## Details
Merge bitcoin-core/gui#944: Fix out-of-bounds read in RPCParseCommandLine on empty command

fef99e6563ae284811904b980069166621c4fa22 qt: fix out-of-bounds read in RPCParseCommandLine on empty command (sayed nabhan)

Pull request description:

  When a console line has no command name (it starts with `)`, or is `()`, `(`, or `,`), RPCParseCommandLine reaches the command-execution branch while the current argument frame is still empty, so `stack.back()[0]` reads out of bounds and the argument list built from `stack.back().begin() + 1` to `end()` is an invalid iterator range (throws std::length_error in practice, UBSan flags the null-pointer reference otherwise).

  The `(` branch already guards the frame with `stack.back().size() > 0`, so I add the same check to the `)`/newline branch and the empty frame is skipped. To be clear, `(` alone isn't safe on master either: it fails via the `\n` branch, not via the `(` branch itself (the state there isn't `STATE_ARGUMENT`), and `,` alone fails the same way.

  Since there's no command to run in any of these cases, the parser now returns `false` so the console reports an invalid command line, consistent with other fully-invalid input like a bare `'` or `"`, rather than silently ignoring it.

  Regression cases added to rpcNestedTests for `)`, `()`, `(` and `,` (all abort on master without the guard), plus `getblockchaininfo)` which stays tolerated.

ACKs for top commit:
  hebasto:
    ACK fef99e6563ae284811904b980069166621c4fa22, tested on Ubuntu 26.04.

Tree-SHA512: 15822a0525402878483d5b2d0fe7b9e27916e514c1a8ad4a697f11b1e5cfe33f5fcd1f089efefb976bcf0d84cdf5166a58a070593924c2d4c2e1f8224d06590f

## Patch
### src/qt/rpcconsole.cpp
```diff
@@ -159,6 +159,7 @@ bool RPCConsole::RPCParseCommandLine(interfaces::Node* node, std::string &strRes
     } state = STATE_EATING_SPACES;
     std::string curarg;
     UniValue lastResult;
+    bool command_parsed = false;
     unsigned nDepthInsideSensitive = 0;
     size_t filter_begin_pos = 0, chpos;
     std::vector<std::pair<size_t, size_t>> filter_ranges;
@@ -290,7 +291,7 @@ bool RPCConsole::RPCParseCommandLine(interfaces::Node* node, std::string &strRes
                         curarg.clear();
                         state = STATE_EATING_SPACES_IN_BRACKETS;
                     }
-                    if ((ch == ')' || ch == '\n') && stack.size() > 0)
+                    if ((ch == ')' || ch == '\n') && stack.size() > 0 && stack.back().size() > 0)
                     {
                         if (fExecute) {
                             // Convert argument list to JSON objects in method-dependent way,
@@ -306,6 +307,7 @@ bool RPCConsole::RPCParseCommandLine(interfaces::Node* node, std::string &strRes
                             lastResult = node->executeRpc(method, params, uri);
                         }
 
+                        command_parsed = true;
                         state = STATE_COMMAND_EXECUTED;
                         curarg.clear();
                     }
@@ -372,8 +374,11 @@ bool RPCConsole::RPCParseCommandLine(interfaces::Node* node, std::string &strRes
                 strResult = lastResult.write(2);
             [[fallthrough]];
         case STATE_ARGUMENT:
-        case STATE_EATING_SPACES:
             return true;
+        case STATE_EATING_SPACES:
+            // Reaching this state without ever parsing a command means the line
+            // held no command name (e.g. ")", "()", "(", ","); treat it as invalid.
+            return command_parsed;
         default: // ERROR to end in one of the other states
             return false;
     }
```

### src/qt/test/rpcnestedtests.cpp
```diff
@@ -134,6 +134,11 @@ void RPCNestedTests::rpcNestedTests()
     QVERIFY_EXCEPTION_THROWN(RPCConsole::RPCExecuteCommandLine(m_node, result, "getblockchaininfo() getblockchaininfo()"), std::runtime_error); //invalid syntax
     RPCConsole::RPCExecuteCommandLine(m_node, result, "getblockchaininfo("); //tolerate non closing brackets if we have no arguments
     RPCConsole::RPCExecuteCommandLine(m_node, result, "getblockchaininfo()()()"); //tolerate non command brackets
+    RPCConsole::RPCExecuteCommandLine(m_node, result, "getblockchaininfo)"); //tolerate a closing bracket after a command
+    QVERIFY(!RPCConsole::RPCExecuteCommandLine(m_node, result, ")")); //reject a closing bracket with no command (empty argument stack)
+    QVERIFY(!RPCConsole::RPCExecuteCommandLine(m_node, result, "()")); //reject empty brackets with no command
+    QVERIFY(!RPCConsole::RPCExecuteCommandLine(m_node, result, "(")); //reject an opening bracket with no command
+    QVERIFY(!RPCConsole::RPCExecuteCommandLine(m_node, result, ",")); //reject a comma with no command
     QVERIFY_EXCEPTION_THROWN(RPCConsole::RPCExecuteCommandLine(m_node, result, "getblockchaininfo(True)"), UniValue); //invalid argument
     QVERIFY_EXCEPTION_THROWN(RPCConsole::RPCExecuteCommandLine(m_node, result, "a(getblockchaininfo(True))"), UniValue); //method not found
     QVERIFY_EXCEPTION_THROWN(RPCConsole::RPCExecuteCommandLine(m_node, result, "rpcNestedTest abc,,abc"), std::runtime_error); //don't tolerate empty arguments when using ,
```
