# [?] Fix panic when using packed config (#488)

## Summary
Severity: Unknown
Chain: Provenance
Component: provenance-io/provenance
Published: 2021-09-16
Source: https://github.com/provenance-io/provenance/commit/d8b5b38f93b1f5f05992f62e0c3e681b9c434434
Type: security-commit

## Details
Fix panic when using packed config (#488)

* [487]: Add a couple unit tests demonstrating the bug.

* [487]: Add changlog entry.

* [487]: Fix bug on providing the telemetry.global-labels to viper from a packed config.

* [487]: In the new unit tests, also assert that the returned config is equal to what was used to write the packed config.

## Patch
### CHANGELOG.md
```diff
@@ -53,6 +53,7 @@ Ref: https://keepachangelog.com/en/1.0.0/
 ### Bug Fixes
 
 * Removed some unneeded code from the persistent record update validation [#471](https://github.com/provenance-io/provenance/issues/471)
+* Fixed packed config loading bug [#487](https://github.com/provenance-io/provenance/issues/487)
 
 ## [v1.7.0](https://github.com/provenance-io/provenance/releases/tag/v1.7.0) - 2021-09-03
 
```

### cmd/provenanced/config/manager.go
```diff
@@ -539,6 +539,25 @@ func addFieldMapToViper(vpr *viper.Viper, fvmap FieldValueMap) error {
 	for k, v := range fvmap {
 		configMap[k] = v.Interface()
 	}
+	// The telemetry.global-labels field in the app config struct is a `[][]string`.
+	// But in serverconfig.GetConfig, it expects viper to return it as a `[]interface{}`.
+	// Then each element of that is expected to also be a `[]interface{}`.
+	// So we need to convert that field before adding it to viper.
+	if gli, hasGL := configMap["telemetry.global-labels"]; hasGL {
+		newv := make([]interface{}, 0)
+		if gli != nil {
+			if gl, ok := gli.([][]string); ok {
+				for _, p := range gl {
+					var newp []interface{}
+					for _, k := range p {
+						newp = append(newp, k)
+					}
+					newv = append(newv, newp)
+				}
+			}
+		}
+		configMap["telemetry.global-labels"] = newv
+	}
 	return vpr.MergeConfigMap(configMap)
 }
 
```

### cmd/provenanced/config/manager_test.go
```diff
@@ -56,6 +56,7 @@ func (s *ConfigManagerTestSuite) makeDummyCmd() *cobra.Command {
 	}
 	dummyCmd.SetOut(ioutil.Discard)
 	dummyCmd.SetErr(ioutil.Discard)
+	dummyCmd.SetArgs([]string{})
 	var err error
 	dummyCmd, err = dummyCmd.ExecuteContextC(ctx)
 	s.Require().NoError(err, "dummy command execution")
@@ -116,3 +117,39 @@ func (s *ConfigManagerTestSuite) TestManagerWriteAppConfigWithIndexEventsThenRea
 	s.Require().NoError(err2, "extracging app config")
 	s.Require().Equal(appConfig.IndexEvents, appConfig2.IndexEvents, "index events before/after")
 }
+
+func (s *ConfigManagerTestSuite) TestPackedConfigCosmosLoadDefaults() {
+	dCmd := s.makeDummyCmd()
+
+	appConfig := serverconfig.DefaultConfig()
+	tmConfig := tmconfig.DefaultConfig()
+	clientConfig := DefaultClientConfig()
+	generateAndWritePackedConfig(dCmd, appConfig, tmConfig, clientConfig, false)
+	s.Require().NoError(loadPackedConfig(dCmd))
+
+	ctx := client.GetClientContextFromCmd(dCmd)
+	vpr := ctx.Viper
+	s.Require().NotPanics(func() {
+		appConfig2 := serverconfig.GetConfig(vpr)
+		s.Assert().Equal(*appConfig, appConfig2)
+	})
+}
+
+func (s *ConfigManagerTestSuite) TestPackedConfigCosmosLoadGlobalLabels() {
+	dCmd := s.makeDummyCmd()
+
+	appConfig := serverconfig.DefaultConfig()
+	appConfig.Telemetry.GlobalLabels = append(appConfig.Telemetry.GlobalLabels, []string{"key1", "value1"})
+	appConfig.Telemetry.GlobalLabels = append(appConfig.Telemetry.GlobalLabels, []string{"key2", "value2"})
+	tmConfig := tmconfig.DefaultConfig()
+	clientConfig := DefaultClientConfig()
+	generateAndWritePackedConfig(dCmd, appConfig, tmConfig, clientConfig, false)
+	s.Require().NoError(loadPackedConfig(dCmd))
+
+	ctx := client.GetClientContextFromCmd(dCmd)
+	vpr := ctx.Viper
+	s.Require().NotPanics(func() {
+		appConfig2 := serverconfig.GetConfig(vpr)
+		s.Assert().Equal(appConfig.Telemetry.GlobalLabels, appConfig2.Telemetry.GlobalLabels)
+	})
+}
```
