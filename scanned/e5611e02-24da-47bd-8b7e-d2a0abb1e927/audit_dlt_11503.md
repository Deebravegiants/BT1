# [?] Merge pull request #2606 from bandprotocol/fix-overflow-result

## Summary
Severity: Unknown
Chain: Oracle
Component: bandprotocol/bandchain
Published: 2020-09-03
Source: https://github.com/bandprotocol/bandchain/commit/257a6c812992f4f604962fd8bf4a0ecbdfb2f20f
Type: security-commit

## Details
Merge pull request #2606 from bandprotocol/fix-overflow-result

Scan: fix overflow text on request index

## Patch
### CHANGELOG_UNRELEASED.md
```diff
@@ -21,6 +21,7 @@
 
 ### Scan
 
+- (bugs) [\#2606](https://github.com/bandprotocol/bandchain/pull/2606) Fix overflow text on request index page
 - (impv) [\#2604](https://github.com/bandprotocol/bandchain/pull/2604) Moved the proposal route to wenchang route
 - (feat) [\#2603](https://github.com/bandprotocol/bandchain/pull/2603) Added `guanyu-poa` on chain id
 - (impv) [\#2599](https://github.com/bandprotocol/bandchain/pull/2599) Polish style on revamp GuanYu part 2
```

### scan/src/components/request/DataReports.re
```diff
@@ -96,15 +96,19 @@ let make = (~reports: array(RequestSub.report_t)) => {
                          idx={externalID ++ exitCode}
                          styles=Styles.mobileCard
                        />
-                     : <Row.Grid alignItems=Row.Center marginBottom=16 key=externalID>
+                     : <Row.Grid alignItems=Row.Start marginBottom=16 key=externalID>
                          <Col.Grid col=Col.Three>
                            <Text value=externalID weight=Text.Medium />
                          </Col.Grid>
                          <Col.Grid col=Col.Three>
                            <Text value=exitCode weight=Text.Medium />
                          </Col.Grid>
                          <Col.Grid col=Col.Six>
-                           <Text value={data |> JsBuffer.toUTF8} weight=Text.Medium />
+                           <Text
+                             value={data |> JsBuffer.toUTF8}
+                             weight=Text.Medium
+                             breakAll=true
+                           />
                          </Col.Grid>
                        </Row.Grid>
                  })
```

### scan/src/pages/RequestIndexPage.re
```diff
@@ -153,10 +153,10 @@ module KVTableContainer = {
                  <TBody.Grid key={fieldName ++ fieldValue} paddingH={`px(24)}>
                    <Row.Grid alignItems=Row.Center minHeight={`px(30)}>
                      <Col.Grid col=Col.Three>
-                       <Text value=fieldName color=Colors.gray7 weight=Text.Thin />
+                       <Text value=fieldName color=Colors.gray7 weight=Text.Thin/>
                      </Col.Grid>
                      <Col.Grid col=Col.Nine>
-                       <Text value=fieldValue color=Colors.gray7 weight=Text.Thin />
+                       <Text value=fieldValue color=Colors.gray7 weight=Text.Thin breakAll=true/>
                      </Col.Grid>
                    </Row.Grid>
                  </TBody.Grid>
```
