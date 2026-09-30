# [?] fix config data race

## Summary
Severity: Unknown
Chain: IPFS
Component: ipfs/kubo
Published: 2018-10-23
Source: https://github.com/ipfs/kubo/commit/56b6277d26bc2c0348a60067a87a37d08cf88ca1
Type: security-commit

## Details
fix config data race

This fixes a data-race in the config.

This does not fix https://github.com/ipfs/go-ipfs/issues/4942 as there's still a
logical race: parallel config updates clobber each other.

License: MIT
Signed-off-by: Steven Allen <steven@stebalien.com>

## Patch
### core/commands/config.go
```diff
@@ -401,15 +401,18 @@ func transformConfig(configRoot string, configName string, transformer config.Tr
 	}
 	defer r.Close()
 
-	cfg, err := r.Config()
+	oldCfg, err := r.Config()
 	if err != nil {
 		return nil, nil, err
 	}
 
 	// make a copy to avoid updating repo's config unintentionally
-	oldCfg := *cfg
-	newCfg := oldCfg
-	err = transformer(&newCfg)
+	newCfg, err := oldCfg.Clone()
+	if err != nil {
+		return nil, nil, err
+	}
+
+	err = transformer(newCfg)
 	if err != nil {
 		return nil, nil, err
 	}
@@ -420,13 +423,13 @@ func transformConfig(configRoot string, configName string, transformer config.Tr
 			return nil, nil, err
 		}
 
-		err = r.SetConfig(&newCfg)
+		err = r.SetConfig(newCfg)
 		if err != nil {
 			return nil, nil, err
 		}
 	}
 
-	return &oldCfg, &newCfg, nil
+	return oldCfg, newCfg, nil
 }
 
 func getConfig(r repo.Repo, key string) (*ConfigField, error) {
```

### repo/fsrepo/fsrepo.go
```diff
@@ -476,9 +476,11 @@ func (r *FSRepo) Close() error {
 	return r.lockfile.Close()
 }
 
+// Config the current config. This function DOES NOT copy the config. The caller
+// MUST NOT modify it without first calling `Clone`.
+//
 // Result when not Open is undefined. The method may panic if it pleases.
 func (r *FSRepo) Config() (*config.Config, error) {
-
 	// It is not necessary to hold the package lock since the repo is in an
 	// opened state. The package lock is _not_ meant to ensure that the repo is
 	// thread-safe. The package lock is only meant to guard against removal and
@@ -546,11 +548,14 @@ func (r *FSRepo) setConfigUnsynced(updated *config.Config) error {
 	if err := serialize.WriteConfigFile(configFilename, mapconf); err != nil {
 		return err
 	}
-	*r.config = *updated // copy so caller cannot modify this private config
+	// Do not use `*r.config = ...`. This will modify the *shared* config
+	// returned by `r.Config`.
+	r.config = updated
 	return nil
 }
 
-// SetConfig updates the FSRepo's config.
+// SetConfig updates the FSRepo's config. The user must not modify the config
+// object after calling this method.
 func (r *FSRepo) SetConfig(updated *config.Config) error {
 
 	// packageLock is held to provide thread-safety.
```
