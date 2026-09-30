# [?] [Neo Fix] fix the store crash issue (#3124)

## Summary
Severity: Unknown
Chain: Neo
Component: neo-project/neo
Published: 2024-02-08
Source: https://github.com/neo-project/neo/commit/95708b5c81661ecf7d78174d639d0f9971eed972
Type: security-commit

## Details
[Neo Fix] fix the store crash issue (#3124)

* fix the store crash issue

* remove loadstore

* Clean changes

---------

Co-authored-by: Fernando Diaz Toledano <shargon@gmail.com>

## Patch
### src/Neo.CLI/CLI/MainService.cs
```diff
@@ -377,8 +377,7 @@ public async void Start(CommandLineOptions options)
             ProtocolSettings protocol = ProtocolSettings.Load("config.json");
             CustomProtocolSettings(options, protocol);
             CustomApplicationSettings(options, Settings.Default);
-            var store = StoreFactory.GetStore(Settings.Default.Storage.Engine, string.Format(Settings.Default.Storage.Path, protocol.Network.ToString("X8")));
-            NeoSystem = new NeoSystem(protocol, store);
+            NeoSystem = new NeoSystem(protocol, Settings.Default.Storage.Engine, string.Format(Settings.Default.Storage.Path, protocol.Network.ToString("X8")));
             NeoSystem.AddService(this);
 
             LocalNode = NeoSystem.LocalNode.Ask<LocalNode>(new LocalNode.GetInstance()).Result;
```

### src/Neo/NeoSystem.cs
```diff
@@ -109,6 +109,16 @@ static NeoSystem()
             Plugin.LoadPlugins();
         }
 
+        /// <summary>
+        /// Initializes a new instance of the <see cref="NeoSystem"/> class.
+        /// </summary>
+        /// <param name="settings">The protocol settings of the <see cref="NeoSystem"/>.</param>
+        /// <param name="storageEngine">The storage engine used to create the <see cref="IStore"/> objects. If this parameter is <see langword="null"/>, a default in-memory storage engine will be used.</param>
+        /// <param name="storagePath">The path of the storage. If <paramref name="storageEngine"/> is the default in-memory storage engine, this parameter is ignored.</param>
+        public NeoSystem(ProtocolSettings settings, string? storageEngine = null, string? storagePath = null) : this(settings, StoreFactory.GetStore(storageEngine ?? nameof(MemoryStore), storagePath))
+        {
+        }
+
         /// <summary>
         /// Initializes a new instance of the <see cref="NeoSystem"/> class.
         /// </summary>
@@ -208,16 +218,6 @@ public void EnsureStopped(IActorRef actor)
             inbox.Receive(TimeSpan.FromMinutes(5));
         }
 
-        /// <summary>
-        /// Loads an <see cref="IStore"/> at the specified path.
-        /// </summary>
-        /// <param name="path">The path of the storage.</param>
-        /// <returns>The loaded <see cref="IStore"/>.</returns>
-        public IStore LoadStore(string path)
-        {
-            return StoreFactory.GetStore(store.GetType().Name, path);
-        }
-
         /// <summary>
         /// Resumes the startup process of <see cref="LocalNode"/>.
         /// </summary>
```

### src/Neo/Persistence/StoreFactory.cs
```diff
@@ -29,9 +29,7 @@ static StoreFactory()
         RegisterProvider(memProvider);
 
         // Default cases
-
         providers.Add("", memProvider);
-        providers.Add(null, memProvider);
     }
 
     public static void RegisterProvider(IStoreProvider provider)
```
