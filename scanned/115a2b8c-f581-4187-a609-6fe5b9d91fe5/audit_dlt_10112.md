# [?] Fix TimeoutException leading to crash on shutdown. (#616)

## Summary
Severity: Unknown
Chain: Neo
Component: neo-project/neo
Published: 2019-03-03
Source: https://github.com/neo-project/neo/commit/f3005e42bae63e7388c4b28a4002b0917f69fd0a
Type: security-commit

## Details
Fix TimeoutException leading to crash on shutdown. (#616)

## Patch
### neo/NeoSystem.cs
```diff
@@ -54,7 +54,7 @@ public void EnsureStoped(IActorRef actor)
             Inbox inbox = Inbox.Create(ActorSystem);
             inbox.Watch(actor);
             ActorSystem.Stop(actor);
-            inbox.Receive(Timeout.InfiniteTimeSpan);
+            inbox.Receive(TimeSpan.FromMinutes(5));
         }
 
         internal void ResumeNodeStartup()
```
