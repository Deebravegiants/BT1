# [?] Fix write target nil dereferences (#14059)

## Summary
Severity: Unknown
Chain: Chainlink
Component: smartcontractkit/chainlink
Published: 2024-08-08
Source: https://github.com/smartcontractkit/chainlink/commit/40f4becb1eab96920d8bfd59019cdb9358a94122
Type: security-commit

## Details
Fix write target nil dereferences (#14059)

* Hardcoded value for call with exact gas

* Record gasProvided in route function

* Add a getter for transmission gas limit

* Update snapshot

* Changeset

* Remove unused import

* Rename to gas limit

* Update gethwrappers

* Uncomment test code

* Remove copy/pasta comment

* Slight rename

* Allow retrying transmissions with more gas

* Only allow retrying failed transmissions

* Update snapshot

* Fix state for InvalidReceiver check

* Check for initial state

* Actually store gas limit provided to receiver

* Update gethwrappers

* Remove unused struct

* Correctly mark invalid receiver when receiver interface unsupported

* Create TransmissionInfo struct

* Update gethwrappers

* Bump gas limit

* Bump gas even more

* Update KeystoneFeedsConsumer.sol to implement IERC165

* Use getTransmissionInfo

* Use TransmissionState to determine if transmission should be created

* Fix test

* Fix trailing line

* Update a mock to the GetLatestValue("getTransmissionInfo") call in a test

* Remove TODO + replace panic with err

* Remove redundant empty lines

* Typo

* Fix nil pointer dereference in write target implementation

* Remove unused constant

* Name mapping values

* Add changeset

---------

Co-authored-by: app-token-issuer-infra-releng[bot] <120227048+app-token-issuer-infra-releng[bot]@users.noreply.github.com>

## Patch
### .changeset/shy-windows-juggle.md
```diff
@@ -0,0 +1,5 @@
+---
+"chainlink": patch
+---
+
+#internal
```

### core/capabilities/targets/write_target.go
```diff
@@ -76,6 +76,10 @@ type EvmConfig struct {
 }
 
 func parseConfig(rawConfig *values.Map) (config EvmConfig, err error) {
+	if rawConfig == nil {
+		return config, fmt.Errorf("missing config field")
+	}
+
 	if err := rawConfig.UnwrapTo(&config); err != nil {
 		return config, err
 	}
@@ -117,6 +121,10 @@ func (cap *WriteTarget) Execute(ctx context.Context, request capabilities.Capabi
 		return nil, err
 	}
 
+	if request.Inputs == nil {
+		return nil, fmt.Errorf("missing inputs field")
+	}
+
 	signedReport, ok := request.Inputs.Underlying[signedReportField]
 	if !ok {
 		return nil, fmt.Errorf("missing required field %s", signedReportField)
```

### core/capabilities/targets/write_target_test.go
```diff
@@ -134,10 +134,10 @@ func TestWriteTarget(t *testing.T) {
 	})
 
 	t.Run("fails with invalid config", func(t *testing.T) {
-		invalidConfig, err := values.NewMap(map[string]any{
+		invalidConfig, err2 := values.NewMap(map[string]any{
 			"Address": "invalid-address",
 		})
-		require.NoError(t, err)
+		require.NoError(t, err2)
 
 		req := capabilities.CapabilityRequest{
 			Metadata: capabilities.RequestMetadata{
@@ -146,7 +146,31 @@ func TestWriteTarget(t *testing.T) {
 			Config: invalidConfig,
 			Inputs: validInputs,
 		}
-		_, err = writeTarget.Execute(ctx, req)
-		require.Error(t, err)
+		_, err2 = writeTarget.Execute(ctx, req)
+		require.Error(t, err2)
+	})
+
+	t.Run("fails with nil config", func(t *testing.T) {
+		req := capabilities.CapabilityRequest{
+			Metadata: capabilities.RequestMetadata{
+				WorkflowID: "test-id",
+			},
+			Config: nil,
+			Inputs: validInputs,
+		}
+		_, err2 := writeTarget.Execute(ctx, req)
+		require.Error(t, err2)
+	})
+
+	t.Run("fails with nil inputs", func(t *testing.T) {
+		req := capabilities.CapabilityRequest{
+			Metadata: capabilities.RequestMetadata{
+				WorkflowID: "test-id",
+			},
+			Config: config,
+			Inputs: nil,
+		}
+		_, err2 := writeTarget.Execute(ctx, req)
+		require.Error(t, err2)
 	})
 }
```
