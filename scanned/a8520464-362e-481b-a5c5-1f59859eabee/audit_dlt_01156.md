# [?] fix: stack overflow in debug_trace (#11487)

## Summary
Severity: Unknown
Chain: Ethereum
Component: NethermindEth/nethermind
Published: 2026-05-12
Source: https://github.com/NethermindEth/nethermind/commit/82f2664d77f3a384e89e69f4d91b874d722f6322
Type: security-commit

## Details
fix: stack overflow in debug_trace (#11487)

* fix stack overflow issue

* remove nullability

* fix formatting

* Update src/Nethermind/Nethermind.Runner/JsonRpc/Startup.cs

Co-authored-by: claude[bot] <209825114+claude[bot]@users.noreply.github.com>

* cut comments

* add input test

---------

Co-authored-by: claude[bot] <209825114+claude[bot]@users.noreply.github.com>

## Patch
### src/Nethermind/Nethermind.Blockchain/Tracing/GethStyle/Custom/Native/Call/NativeCallTracerCallFrameConverter.cs
```diff
@@ -2,6 +2,7 @@
 // SPDX-License-Identifier: LGPL-3.0-only
 
 using System;
+using System.Collections.Generic;
 using System.Text.Json;
 using System.Text.Json.Serialization;
 using Nethermind.Serialization.Json;
@@ -15,78 +16,111 @@ public override void Write(Utf8JsonWriter writer, NativeCallTracerCallFrame valu
         NumberConversion previousValue = ForcedNumberConversion.Value;
         try
         {
-            writer.WriteStartObject();
-
             ForcedNumberConversion.Value = NumberConversion.Hex;
-            writer.WritePropertyName("type"u8);
-            JsonSerializer.Serialize(writer, Enum.GetName(value.Type), options);
 
-            writer.WritePropertyName("from"u8);
-            JsonSerializer.Serialize(writer, value.From, options);
+            Stack<(NativeCallTracerCallFrame Frame, int NextChild)> work = new();
+            work.Push((value, -1));
 
-            if (value.To is not null)
+            while (work.Count > 0)
             {
-                writer.WritePropertyName("to"u8);
-                JsonSerializer.Serialize(writer, value.To, options);
+                (NativeCallTracerCallFrame frame, int nextChild) = work.Pop();
+
+                if (nextChild == -1)
+                {
+                    WriteFrameHeader(writer, frame, options);
+
+                    if (frame.Calls is { Count: > 0 })
+                    {
+                        writer.WritePropertyName("calls"u8);
+                        writer.WriteStartArray();
+                        nextChild = 0;
+                    }
+                    else
+                    {
+                        writer.WriteEndObject();
+                        continue;
+                    }
+                }
+
+                if (nextChild < frame.Calls.Count)
+                {
+                    NativeCallTracerCallFrame child = frame.Calls[nextChild];
+                    work.Push((frame, nextChild + 1));
+                    work.Push((child, -1));
+                }
+                else
+                {
+                    writer.WriteEndArray();
+                    writer.WriteEndObject();
+                }
             }
+        }
+        finally
+        {
+            ForcedNumberConversion.Value = previousValue;
+        }
+    }
 
-            if (value.Value is not null)
-            {
-                writer.WritePropertyName("value"u8);
-                JsonSerializer.Serialize(writer, value.Value, options);
-            }
+    private static void WriteFrameHeader(Utf8JsonWriter writer, NativeCallTracerCallFrame value, JsonSerializerOptions options)
+    {
+        writer.WriteStartObject();
 
-            writer.WritePropertyName("gas"u8);
-            JsonSerializer.Serialize(writer, value.Gas, options);
+        writer.WritePropertyName("type"u8);
+        JsonSerializer.Serialize(writer, Enum.GetName(value.Type), options);
 
-            writer.WritePropertyName("gasUsed"u8);
-            JsonSerializer.Serialize(writer, value.GasUsed, options);
+        writer.WritePropertyName("from"u8);
+        JsonSerializer.Serialize(writer, value.From, options);
 
-            writer.WritePropertyName("input"u8);
-            if (value.Input is null || value.Input.Count == 0)
-            {
-                writer.WriteStringValue("0x"u8);
-            }
-            else
-            {
-                JsonSerializer.Serialize(writer, value.Input.AsReadOnlyMemory(), options);
-            }
+        if (value.To is not null)
+        {
+            writer.WritePropertyName("to"u8);
+            JsonSerializer.Serialize(writer, value.To, options);
+        }
 
-            if (value.Output?.Count > 0)
-            {
-                writer.WritePropertyName("output"u8);
-                JsonSerializer.Serialize(writer, value.Output.AsReadOnlyMemory(), options);
-            }
+        if (value.Value is not null)
+        {
+            writer.WritePropertyName("value"u8);
+            JsonSerializer.Serialize(writer, value.Value, options);
+        }
 
-            if (value.Error is not null)
-            {
-                writer.WritePropertyName("error"u8);
-                JsonSerializer.Serialize(writer, value.Error, options);
-            }
+        writer.WritePropertyName("gas"u8);
+        JsonSerializer.Serialize(writer, value.Gas, options);
 
-            if (value.RevertReason is not null)
-            {
-                writer.WritePropertyName("revertReason"u8);
-                JsonSerializer.Serialize(writer, value.RevertReason, options);
-            }
+        writer.WritePropertyName("gasUsed"u8);
+        JsonSerializer.Serialize(writer, value.GasUsed, options);
 
-            if (value.Logs?.Count > 0)
-            {
-                writer.WritePropertyName("logs"u8);
-                JsonSerializer.Serialize(writer, value.Logs.AsMemory(), options);
-            }
+        writer.WritePropertyName("input"u8);
+        if (value.Input is null || value.Input.Count == 0)
+        {
+            writer.WriteStringValue("0x"u8);
+        }
+        else
+        {
+            JsonSerializer.Serialize(writer, value.Input.AsReadOnlyMemory(), options);
+        }
 
-            if (value.Calls?.Count > 0)
-            {
-                writer.WritePropertyName("calls"u8);
-                JsonSerializer.Serialize(writer, value.Calls.AsMemory(), options);
-            }
+        if (value.Output?.Count > 0)
+        {
+            writer.WritePropertyName("output"u8);
+            JsonSerializer.Serialize(writer, value.Output.AsReadOnlyMemory(), options);
+        }
 
-            writer.WriteEndObject();
+        if (value.Error is not null)
+        {
+            writer.WritePropertyName("error"u8);
+            JsonSerializer.Serialize(writer, value.Error, options);
         }
-        finally
+
+        if (value.RevertReason is not null)
         {
-            ForcedNumberConversion.Value = previousValue;
+            writer.WritePropertyName("revertReason"u8);
+            JsonSerializer.Serialize(writer, value.RevertReason, options);
+        }
+
+        if (value.Logs?.Count > 0)
+        {
+            writer.WritePropertyName("logs"u8);
+            JsonSerializer.Serialize(writer, value.Logs.AsMemory(), options);
         }
     }
 
```

### src/Nethermind/Nethermind.Evm.Test/Tracing/GethLikeCallTracerTests.cs
```diff
@@ -2,11 +2,14 @@
 // SPDX-License-Identifier: LGPL-3.0-only
 
 using System;
+using System.IO;
+using System.Text;
 using System.Text.Json;
 using Nethermind.Core;
 using Nethermind.Core.Extensions;
 using Nethermind.Core.Test.Builders;
 using Nethermind.Blockchain.Tracing.GethStyle;
+using Nethermind.Blockchain.Tracing.GethStyle.Custom;
 using Nethermind.Blockchain.Tracing.GethStyle.Custom.Native.Call;
 using Nethermind.Evm.TransactionProcessing;
 using Nethermind.Serialization.Json;
@@ -633,6 +636,92 @@ public void Test_CallTrace_TopLevelCreate_WithLog_DeployContractFailure_LogsClea
     }
 
 
+    [Test]
+    public void Test_CallTrace_DeepNesting_DoesNotThrow()
+    {
+        using NativeCallTracerCallFrame root = BuildLinearCallChain(VirtualMachineStatics.MaxCallDepth);
+        GethLikeCustomTrace customTrace = new() { Value = root };
+
+        Assert.That(
+            () => JsonSerializer.Serialize(customTrace, EthereumJsonSerializer.JsonOptions),
+            Throws.Nothing);
+    }
+
+    [Test]
+    public void Test_CallTrace_DeepNesting_StreamedJsonIsComplete()
+    {
+        int depth = VirtualMachineStatics.MaxCallDepth;
+        using NativeCallTracerCallFrame root = BuildLinearCallChain(depth);
+        GethLikeCustomTrace customTrace = new() { Value = root };
+
+        using MemoryStream stream = new();
+        using (Utf8JsonWriter writer = new(stream, new JsonWriterOptions { SkipValidation = true, MaxDepth = EthereumJsonSerializer.DefaultMaxDepth }))
+        {
+            JsonSerializer.Serialize(writer, customTrace, EthereumJsonSerializer.JsonOptions);
+        }
+
+        string output = Encoding.UTF8.GetString(stream.ToArray());
+
+        using JsonDocument document = JsonDocument.Parse(output, new JsonDocumentOptions { MaxDepth = EthereumJsonSerializer.DefaultMaxDepth });
+        JsonElement element = document.RootElement;
+        int observed = 1;
+        while (element.TryGetProperty("calls", out JsonElement calls))
+        {
+            Assert.That(calls.GetArrayLength(), Is.EqualTo(1), $"frame at depth {observed} should have one child");
+            element = calls[0];
+            observed++;
+        }
+        Assert.That(observed, Is.EqualTo(depth), "deserialized frame chain depth should match the constructed depth");
+    }
+
+    [Test]
+    public void Test_CallTrace_DeepNesting_FailsBeyondMaxDepth()
+    {
+        int boundary = EthereumJsonSerializer.DefaultMaxDepth / 2;
+
+        using NativeCallTracerCallFrame atBoundary = BuildLinearCallChain(boundary);
+        Assert.That(
+            () => JsonSerializer.Serialize(new GethLikeCustomTrace { Value = atBoundary }, EthereumJsonSerializer.JsonOptions),
+            Throws.Nothing,
+            $"chain of {boundary} frames must serialize");
+
+        using NativeCallTracerCallFrame justOver = BuildLinearCallChain(boundary + 1);
+        Assert.That(
+            () => JsonSerializer.Serialize(new GethLikeCustomTrace { Value = justOver }, EthereumJsonSerializer.JsonOptions),
+            Throws.TypeOf<JsonException>()
+                .With.InnerException.TypeOf<InvalidOperationException>()
+                .And.InnerException.Message.EqualTo(
+                    $"CurrentDepth ({EthereumJsonSerializer.DefaultMaxDepth}) is equal to or larger than the maximum allowed depth of {EthereumJsonSerializer.DefaultMaxDepth}. Cannot write the next JSON object or array."),
+            $"chain of {boundary + 1} frames must throw the writer's depth-too-large error");
+    }
+
+    private static NativeCallTracerCallFrame BuildLinearCallChain(int depth)
+    {
+        NativeCallTracerCallFrame root = new()
+        {
+            Type = Instruction.CALL,
+            From = TestItem.AddressA,
+            To = TestItem.AddressB,
+            Gas = 100_000,
+            GasUsed = 50_000,
+        };
+        NativeCallTracerCallFrame current = root;
+        for (int i = 1; i < depth; i++)
+        {
+            NativeCallTracerCallFrame child = new()
+            {
+                Type = Instruction.CALL,
+                From = TestItem.AddressA,
+                To = TestItem.AddressB,
+                Gas = 100_000,
+                GasUsed = 50_000,
+            };
+            current.Calls.Add(child);
+            current = child;
+        }
+        return root;
+    }
+
     private byte[] CreateNestedCallsCode(bool revertParentCall = false, bool revertCreateCall = false)
     {
         byte[] deployedCode = new byte[3];
```

### src/Nethermind/Nethermind.JsonRpc.Test/JsonRpcProcessorTests.cs
```diff
@@ -7,6 +7,7 @@
 using System.IO.Pipelines;
 using System.Linq;
 using System.Text;
+using System.Text.Json;
 using System.Threading;
 using System.Threading.Tasks;
 using FluentAssertions;
@@ -567,4 +568,68 @@ public async Task Resolved_method_response_keeps_original_method_name_in_report(
         result[0].Report!.Value.Success.Should().BeTrue();
         result.DisposeItems();
     }
+
+    [TestCase(50, false, TestName = "Input below the 64-depth limit is accepted")]
+    [TestCase(65, true, TestName = "Input above the 64-depth limit is rejected as parse error")]
+    public async Task Input_depth_is_bounded_by_reader_default_max_depth(int paramNestingDepth, bool expectParseError)
+    {
+        JsonRpcRequest? captured = null;
+        IJsonRpcService service = Substitute.For<IJsonRpcService>();
+        service.SendRequestAsync(Arg.Any<JsonRpcRequest>(), Arg.Any<JsonRpcContext>())
+            .Returns(ci =>
+            {
+                captured = ci.Arg<JsonRpcRequest>();
+                return new JsonRpcSuccessResponse { Id = captured.Id };
+            });
+        service.GetErrorResponse(0, null!).ReturnsForAnyArgs(_errorResponse);
+        service.GetErrorResponse(0, null!, null!, null!).ReturnsForAnyArgs(_errorResponse);
+
+        JsonRpcConfig config = new() { RpcRecorderState = RpcRecorderState.None };
+        JsonRpcProcessor processor = new(service, config, Substitute.For<IFileSystem>(), LimboLogs.Instance);
+
+        string nested = BuildNestedArrayParams(paramNestingDepth);
+        string request = $"{{\"id\":1,\"jsonrpc\":\"2.0\",\"method\":\"eth_getTransactionCount\",\"params\":[{nested}]}}";
+
+        List<JsonRpcResult> result = await processor.ProcessAsync(request, new JsonRpcContext(RpcEndpoint.Http)).ToListAsync();
+
+        result.Should().HaveCount(1);
+
+        if (expectParseError)
+        {
+            result[0].Response.Should().BeSameAs(_errorResponse);
+            captured.Should().BeNull("a depth-rejected request must never reach the service");
+        }
+        else
+        {
+            result[0].Response.Should().BeOfType<JsonRpcSuccessResponse>();
+            result[0].Response!.Id.Should().Be(1);
+
+            captured.Should().NotBeNull();
+            captured!.Method.Should().Be("eth_getTransactionCount");
+
+            JsonElement paramsArr = captured.Params;
+            paramsArr.ValueKind.Should().Be(JsonValueKind.Array);
+            paramsArr.GetArrayLength().Should().Be(1);
+
+            int observedDepth = 1;
+            JsonElement node = paramsArr[0];
+            while (node.ValueKind == JsonValueKind.Array && node.GetArrayLength() > 0)
+            {
+                node = node[0];
+                observedDepth++;
+            }
+            node.ValueKind.Should().Be(JsonValueKind.Array);
+            node.GetArrayLength().Should().Be(0, "innermost array of the constructed chain is empty");
+            observedDepth.Should().Be(paramNestingDepth);
+        }
+        result.DisposeItems();
+    }
+
+    private static string BuildNestedArrayParams(int depth)
+    {
+        StringBuilder sb = new(depth * 2);
+        for (int i = 0; i < depth; i++) sb.Append('[');
+        for (int i = 0; i < depth; i++) sb.Append(']');
+        return sb.ToString();
+    }
 }
```

### src/Nethermind/Nethermind.JsonRpc/IJsonRpcConfig.cs
```diff
@@ -157,7 +157,7 @@ public interface IJsonRpcConfig : IConfig
     [ConfigItem(Description = "The max number of JSON-RPC requests in a batch.", DefaultValue = "1024")]
     int MaxBatchSize { get; set; }
 
-    [ConfigItem(Description = "The maximum depth of JSON response object tree.", DefaultValue = "128")]
+    [ConfigItem(Description = "The maximum depth of JSON response object tree.", DefaultValue = "4096")]
     int JsonSerializationMaxDepth { get; set; }
 
     [ConfigItem(Description = "The max batch size limit for batched JSON-RPC calls.", DefaultValue = "33554432")]
```

### src/Nethermind/Nethermind.Serialization.Json/EthereumJsonSerializer.cs
```diff
@@ -18,15 +18,19 @@ namespace Nethermind.Serialization.Json
 {
     public sealed class EthereumJsonSerializer : IJsonSerializer
     {
-        public const int DefaultMaxDepth = 128;
+        // Must accommodate the deepest possible callTracer output: each NativeCallTracerCallFrame
+        // contributes ~2 JSON levels (object + "calls" array), the EVM allows up to MaxCallDepth=1024
+        // (Yellow Paper / Nethermind.Evm.VirtualMachine.MaxCallDepth), plus a few levels of JSON-RPC
+        // envelope. 4096 leaves comfortable headroom.
+        public const int DefaultMaxDepth = 4096;
         private static readonly object _globalOptionsLock = new();
 
         private static readonly List<JsonConverter> _additionalConverters = new();
         private static readonly List<IJsonTypeInfoResolver> _additionalResolvers = new();
         private static bool _strictHexFormat;
         private static int _optionsVersion;
 
-        private readonly int? _maxDepth;
+        private readonly int _maxDepth;
         private readonly JsonConverter[] _instanceConverters;
         private readonly object _instanceOptionsLock = new();
 
@@ -178,8 +182,7 @@ public long Serialize<T>(Stream stream, T value, bool indented = false, bool lea
 
         private JsonWriterOptions CreateWriterOptions(bool indented)
         {
-            JsonWriterOptions writerOptions = new() { SkipValidation = true, Indented = indented };
-            writerOptions.MaxDepth = _maxDepth ?? writerOptions.MaxDepth;
+            JsonWriterOptions writerOptions = new() { SkipValidation = true, Indented = indented, MaxDepth = _maxDepth };
             return writerOptions;
         }
 
@@ -238,8 +241,8 @@ private void EnsureInstanceOptionsCurrent()
 
         private void RefreshInstanceOptions()
         {
-            _jsonOptions = CreateOptions(indented: false, instanceConverters: _instanceConverters, maxDepth: _maxDepth ?? DefaultMaxDepth);
-            _jsonOptionsIndented = CreateOptions(indented: true, instanceConverters: _instanceConverters, maxDepth: _maxDepth ?? DefaultMaxDepth);
+            _jsonOptions = CreateOptions(indented: false, instanceConverters: _instanceConverters, maxDepth: _maxDepth);
+            _jsonOptionsIndented = CreateOptions(indented: true, instanceConverters: _instanceConverters, maxDepth: _maxDepth);
             _instanceOptionsVersion = Volatile.Read(ref _optionsVersion);
         }
 
```
