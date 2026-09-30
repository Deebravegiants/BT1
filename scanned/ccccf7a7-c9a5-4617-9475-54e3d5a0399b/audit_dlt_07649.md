# [?] fix: fix data race on _requestCount in MessageDictionary (#10813)

## Summary
Severity: Unknown
Chain: Ethereum
Component: NethermindEth/nethermind
Published: 2026-03-13
Source: https://github.com/NethermindEth/nethermind/commit/41ce0bc9b84e15ed1cc1b544491952569b063c3f
Type: security-commit

## Details
fix: fix data race on _requestCount in MessageDictionary (#10813)

Update MessageDictionary.cs

## Patch
### src/Nethermind/Nethermind.Network/P2P/MessageDictionary.cs
```diff
@@ -6,6 +6,7 @@
 using System.Collections.Generic;
 using System.Diagnostics;
 using System.Diagnostics.CodeAnalysis;
+using System.Threading;
 using System.Threading.Tasks;
 using Nethermind.Core.Exceptions;
 using Nethermind.Core.Extensions;
@@ -36,7 +37,7 @@ public class MessageDictionary<T66Msg, TData>(Action<T66Msg> send, TimeSpan? old
 
     public void Send(Request<T66Msg, TData> request)
     {
-        if (_requestCount >= MaxConcurrentRequest)
+        if (Volatile.Read(ref _requestCount) >= MaxConcurrentRequest)
         {
             request.Message.TryDispose();
             ThrowTooManyOutstandingRequests();
@@ -45,7 +46,7 @@ public void Send(Request<T66Msg, TData> request)
 
         if (_requests.TryAdd(request.Message.RequestId, request))
         {
-            _requestCount++;
+            Interlocked.Increment(ref _requestCount);
             request.StartMeasuringTime();
             send(request.Message);
 
@@ -78,22 +79,22 @@ private async Task CleanOldRequests()
                 {
                     if (_requests.TryRemove(requestIdValues.Key, out Request<T66Msg, TData> request))
                     {
-                        _requestCount--;
+                        Interlocked.Decrement(ref _requestCount);
                         // Unblock waiting thread.
                         request.CompletionSource.TrySetException(new TimeoutException("No response received"));
                     }
                 }
             }
 
-            if (_requestCount == 0) break;
+            if (Volatile.Read(ref _requestCount) == 0) break;
         }
     }
 
     public void Handle(long id, TData data, long size)
     {
         if (_requests.TryRemove(id, out Request<T66Msg, TData>? request))
         {
-            _requestCount--;
+            Interlocked.Decrement(ref _requestCount);
             request.ResponseSize = size;
             request.CompletionSource.TrySetResult(data);
         }
```
