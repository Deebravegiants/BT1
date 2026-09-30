# [?] bump chainlink-env to fix a test race condition around waiting for po… (#8317)

## Summary
Severity: Unknown
Chain: Bridge
Component: smartcontractkit/ccip
Published: 2023-01-26
Source: https://github.com/smartcontractkit/ccip/commit/81892067c1abe7a898ee69a45888e243f73172a3
Type: security-commit

## Details
bump chainlink-env to fix a test race condition around waiting for po… (#8317)

* bump chainlink-env to fix a test race condition around waiting for pods to be ready

* Bump to latest and save the failure artifacts

Co-authored-by: Adam Hamrick <adam.hamrick@smartcontract.com>

## Patch
### .github/workflows/integration-tests.yml
```diff
@@ -201,6 +201,13 @@ jobs:
         uses: smartcontractkit/chainlink-github-actions/chainlink-testing-framework/cleanup@e72f0a768ac934afce498a802de893d89b12802f # v2.1.1
         with:
           triggered_by: ${{ env.TEST_TRIGGERED_BY }}-${{ matrix.product.name }}
+      - name: Upload test log
+        uses: actions/upload-artifact@0b7f8abb1508181956e8e162db84b466c27e18ce # v3.1.2
+        if: failure()
+        with:
+          name: test-log-${{ matrix.product.name }}
+          path: /tmp/gotest.log
+          retention-days: 7
       - name: Collect Metrics
         if: always()
         id: collect-gha-metrics
```

### integration-tests/go.mod
```diff
@@ -12,7 +12,7 @@ require (
 	github.com/satori/go.uuid v1.2.0
 	github.com/slack-go/slack v0.11.4
 	github.com/smartcontractkit/chainlink v1.10.0
-	github.com/smartcontractkit/chainlink-env v0.3.0
+	github.com/smartcontractkit/chainlink-env v0.3.6
 	github.com/smartcontractkit/chainlink-testing-framework v1.9.2
 	github.com/smartcontractkit/libocr v0.0.0-20221209172631-568a30f68407
 	github.com/smartcontractkit/ocr2keepers v0.6.6
```

### integration-tests/go.sum
```diff
@@ -1599,8 +1599,8 @@ github.com/sirupsen/logrus v1.9.0 h1:trlNQbNUG3OdDrDil03MCb1H2o9nJ1x4/5LYw7byDE0
 github.com/sirupsen/logrus v1.9.0/go.mod h1:naHLuLoDiP4jHNo9R0sCBMtWGeIprob74mVsIT4qYEQ=
 github.com/slack-go/slack v0.11.4 h1:ojSa7KlPm3PqY2AomX4VTxEsK5eci5JaxCjlzGV5zoM=
 github.com/slack-go/slack v0.11.4/go.mod h1:hlGi5oXA+Gt+yWTPP0plCdRKmjsDxecdHxYQdlMQKOw=
-github.com/smartcontractkit/chainlink-env v0.3.0 h1:HfyjiXeWUEDTI5vM7asSpTzqrx/9R71915MNEta+Ihw=
-github.com/smartcontractkit/chainlink-env v0.3.0/go.mod h1:zspYFdXS57CzKkpcLkFEPuMQHOmI3L9H5idoPxobxRM=
+github.com/smartcontractkit/chainlink-env v0.3.6 h1:BsoK/XbZCsoBoKiKwyt4uCI1l/XQigHv3D6dYooXn6M=
+github.com/smartcontractkit/chainlink-env v0.3.6/go.mod h1:zspYFdXS57CzKkpcLkFEPuMQHOmI3L9H5idoPxobxRM=
 github.com/smartcontractkit/chainlink-relay v0.1.6-0.20221025223751-9b407cff57eb h1:NF6//JILgK8AeLkknJFEVsVRt+VqwNnxJ4SLpHKje9c=
 github.com/smartcontractkit/chainlink-relay v0.1.6-0.20221025223751-9b407cff57eb/go.mod h1:v/QSrVm3z4/aPz/PLB6da05B/r4MHZy0/jder7iPxkQ=
 github.com/smartcontractkit/chainlink-solana v1.0.2-0.20220930034647-edd5a863b876 h1:uctLwzPqXUbWWcOiZaltKNtb2XfIDVE1yQ04uLZ3N7Q=
```
