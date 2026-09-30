# [?] qml: fix InfoTextArea text sometimes out of bounds

## Summary
Severity: Unknown
Chain: Bitcoin
Component: spesmilo/electrum
Published: 2024-11-01
Source: https://github.com/spesmilo/electrum/commit/2134fcc4dcd1799d86ce90965bdfe4b702c9767b
Type: security-commit

## Details
qml: fix InfoTextArea text sometimes out of bounds

## Patch
### electrum/gui/qml/components/controls/InfoTextArea.qml
```diff
@@ -72,7 +72,6 @@ TextHighlightPane {
         Label {
             id: infotext
             Layout.fillWidth: true
-            width: parent.width
             wrapMode: Text.Wrap
         }
     }
```
