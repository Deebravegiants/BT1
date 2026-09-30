# [?] Patch HLS so it doesn't crash on macOS (#3023)

## Summary
Severity: Unknown
Chain: Cardano
Component: IntersectMBO/plutus
Published: 2021-04-16
Source: https://github.com/IntersectMBO/plutus/commit/11981b29a871b575a073f75a0b611db5f29d230b
Type: security-commit

## Details
Patch HLS so it doesn't crash on macOS (#3023)

* Patch HLS so it doesn't crash on macOS

* Only patch HLS on macOS

* Add comment to issue this workaround is for.

## Patch
### nix/patches/haskell-language-server-dynamic.patch
```diff
@@ -0,0 +1,31 @@
+diff --git a/haskell-language-server.cabal b/haskell-language-server.cabal
+index b39fbdff..5439dfff 100644
+--- a/haskell-language-server.cabal
++++ b/haskell-language-server.cabal
+@@ -79,7 +79,7 @@ library
+     , unordered-containers
+     , aeson-pretty
+
+-  ghc-options:      -Wall -Wredundant-constraints -Wno-name-shadowing -Wno-unticked-promoted-constructors
++  ghc-options:      -Wall -Wredundant-constraints -Wno-name-shadowing -Wno-unticked-promoted-constructors -dynamic
+
+   if flag(pedantic)
+     ghc-options: -Werror
+@@ -296,7 +296,7 @@ executable haskell-language-server
+   other-modules:    Plugins
+
+   ghc-options:
+-    -threaded -Wall -Wno-name-shadowing -Wredundant-constraints
++    -threaded -Wall -Wno-name-shadowing -Wredundant-constraints  -dynamic
+     -- allow user RTS overrides
+     -rtsopts
+     -- disable idle GC
+@@ -349,7 +349,7 @@ executable haskell-language-server-wrapper
+   other-modules:    Paths_haskell_language_server
+   autogen-modules:  Paths_haskell_language_server
+   ghc-options:
+-    -threaded -Wall -Wno-name-shadowing -Wredundant-constraints
++    -threaded -Wall -Wno-name-shadowing -Wredundant-constraints -dynamic
+     -- allow user RTS overrides
+     -rtsopts
+     -- disable idle GC
```

### nix/pkgs/haskell/extra.nix
```diff
@@ -93,6 +93,8 @@
       else "0mgxp1ja7rjh3qnf5ph4a4phncsd3yh04cxmdsg8baczx7jndfaf";
     modules = [{
       packages.ghcide.patches = [ ../../patches/ghcide_partial_iface.patch ];
+      # Workaround for https://github.com/haskell/haskell-language-server/issues/1160
+      packages.haskell-language-server.patches = lib.mkIf stdenv.isDarwin [ ../../patches/haskell-language-server-dynamic.patch ];
     }];
   };
   in { inherit (project.hsPkgs) haskell-language-server hie-bios implicit-hie; }
```
