# [?] CORDA-3688: Apply @Named annotation to CRaSH commands to fix usage messages. (#6126)

## Summary
Severity: Unknown
Chain: Corda
Component: corda/corda
Published: 2020-04-03
Source: https://github.com/corda/corda/commit/032f008e7ebd468973f2639d942f7519f6d51add
Type: security-commit

## Details
CORDA-3688: Apply @Named annotation to CRaSH commands to fix usage messages. (#6126)

## Patch
### tools/shell/src/main/java/net/corda/tools/shell/AttachmentShellCommand.java
```diff
@@ -2,10 +2,12 @@
 
 import org.crsh.cli.Command;
 import org.crsh.cli.Man;
+import org.crsh.cli.Named;
 import org.crsh.cli.Usage;
 
 import static net.corda.tools.shell.InteractiveShell.runAttachmentTrustInfoView;
 
+@Named("attachments")
 public class AttachmentShellCommand extends InteractiveShellCommand {
 
     @Command
```

### tools/shell/src/main/java/net/corda/tools/shell/CheckpointShellCommand.java
```diff
@@ -2,10 +2,12 @@
 
 import org.crsh.cli.Command;
 import org.crsh.cli.Man;
+import org.crsh.cli.Named;
 import org.crsh.cli.Usage;
 
 import static net.corda.tools.shell.InteractiveShell.*;
 
+@Named("checkpoints")
 public class CheckpointShellCommand extends InteractiveShellCommand {
 
     @Command
```

### tools/shell/src/main/java/net/corda/tools/shell/FlowShellCommand.java
```diff
@@ -26,6 +26,7 @@
                 "command with either a full class name, or a substring of the class name that's unambiguous. The parameters to the \n" +
                 "flow constructors (the right one is picked automatically) are then specified using the same syntax as for the run command."
 )
+@Named("flow")
 public class FlowShellCommand extends InteractiveShellCommand {
 
     private static final Logger logger = LoggerFactory.getLogger(FlowShellCommand.class);
```

### tools/shell/src/main/java/net/corda/tools/shell/HashLookupShellCommand.java
```diff
@@ -6,6 +6,7 @@
 import org.crsh.cli.Argument;
 import org.crsh.cli.Command;
 import org.crsh.cli.Man;
+import org.crsh.cli.Named;
 import org.crsh.cli.Usage;
 import org.crsh.text.Color;
 import org.crsh.text.Decoration;
@@ -15,6 +16,7 @@
 import java.util.List;
 import java.util.Optional;
 
+@Named("hashLookup")
 public class HashLookupShellCommand extends InteractiveShellCommand {
     private static Logger logger = LoggerFactory.getLogger(HashLookupShellCommand.class);
 
```

### tools/shell/src/main/java/net/corda/tools/shell/OutputFormatCommand.java
```diff
@@ -7,6 +7,7 @@
 import org.crsh.cli.Argument;
 import org.crsh.cli.Command;
 import org.crsh.cli.Man;
+import org.crsh.cli.Named;
 import org.crsh.cli.Usage;
 import org.crsh.command.InvocationContext;
 import org.crsh.command.ScriptException;
@@ -16,6 +17,7 @@
 
 @Man("Allows you to see and update the format that's currently used for the commands' output.")
 @Usage("Allows you to see and update the format that's currently used for the commands' output.")
+@Named("output-format")
 public class OutputFormatCommand extends InteractiveShellCommand {
 
     public OutputFormatCommand() {}
```

### tools/shell/src/main/java/net/corda/tools/shell/RunShellCommand.java
```diff
@@ -7,6 +7,7 @@
 import org.crsh.cli.Argument;
 import org.crsh.cli.Command;
 import org.crsh.cli.Man;
+import org.crsh.cli.Named;
 import org.crsh.cli.Usage;
 import org.crsh.command.InvocationContext;
 import org.jetbrains.annotations.NotNull;
@@ -23,6 +24,7 @@
 // Note that this class cannot be converted to Kotlin because CRaSH does not understand InvocationContext<Map<?, ?>> which
 // is the closest you can get in Kotlin to raw types.
 
+@Named("run")
 public class RunShellCommand extends InteractiveShellCommand {
 
     private static final Logger logger = LoggerFactory.getLogger(RunShellCommand.class);
```

### tools/shell/src/main/java/net/corda/tools/shell/StartShellCommand.java
```diff
@@ -12,6 +12,7 @@
 
 import static java.util.stream.Collectors.joining;
 
+@Named("start")
 public class StartShellCommand extends InteractiveShellCommand {
 
     private static Logger logger = LoggerFactory.getLogger(StartShellCommand.class);
```
