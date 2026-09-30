# [?] plugin: fix non-deterministic loading order

## Summary
Severity: Unknown
Chain: IPFS
Component: ipfs/kubo
Published: 2023-05-31
Source: https://github.com/ipfs/kubo/commit/99fdaa1b4dc46e369a72989d2e1b3a6bfbf1a11c
Type: security-commit

## Details
plugin: fix non-deterministic loading order

fix #9909

## Patch
### plugin/loader/loader.go
```diff
@@ -87,15 +87,15 @@ func (ls loaderState) String() string {
 //  5. Call Close to close all plugins.
 type PluginLoader struct {
 	state   loaderState
-	plugins map[string]plugin.Plugin
+	plugins []plugin.Plugin
 	started []plugin.Plugin
 	config  config.Plugins
 	repo    string
 }
 
 // NewPluginLoader creates new plugin loader
 func NewPluginLoader(repo string) (*PluginLoader, error) {
-	loader := &PluginLoader{plugins: make(map[string]plugin.Plugin, len(preloadPlugins)), repo: repo}
+	loader := &PluginLoader{plugins: make([]plugin.Plugin, 0, len(preloadPlugins)), repo: repo}
 	if repo != "" {
 		cfg, err := cserialize.Load(filepath.Join(repo, config.DefaultConfigFile))
 		switch err {
@@ -106,6 +106,7 @@ func NewPluginLoader(repo string) (*PluginLoader, error) {
 			return nil, err
 		}
 	}
+
 	for _, v := range preloadPlugins {
 		if err := loader.Load(v); err != nil {
 			return nil, err
@@ -140,18 +141,22 @@ func (loader *PluginLoader) Load(pl plugin.Plugin) error {
 	}
 
 	name := pl.Name()
-	if ppl, ok := loader.plugins[name]; ok {
-		// plugin is already loaded
-		return fmt.Errorf(
-			"plugin: %s, is duplicated in version: %s, "+
-				"while trying to load dynamically: %s",
-			name, ppl.Version(), pl.Version())
+
+	for _, p := range loader.plugins {
+		if p.Name() == name {
+			// plugin is already loaded
+			return fmt.Errorf(
+				"plugin: %s, is duplicated in version: %s, "+
+					"while trying to load dynamically: %s",
+				name, p.Version(), pl.Version())
+		}
 	}
+
 	if loader.config.Plugins[name].Disabled {
 		log.Infof("not loading disabled plugin %s", name)
 		return nil
 	}
-	loader.plugins[name] = pl
+	loader.plugins = append(loader.plugins, pl)
 	return nil
 }
 
@@ -219,10 +224,10 @@ func (loader *PluginLoader) Initialize() error {
 	if err := loader.transition(loaderLoading, loaderInitializing); err != nil {
 		return err
 	}
-	for name, p := range loader.plugins {
+	for _, p := range loader.plugins {
 		err := p.Init(&plugin.Environment{
 			Repo:   loader.repo,
-			Config: loader.config.Plugins[name].Config,
+			Config: loader.config.Plugins[p.Name()].Config,
 		})
 		if err != nil {
 			loader.state = loaderFailed
```
