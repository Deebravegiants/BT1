# [?] Reset crash fix by not autoseeding  (#226)

## Summary
Severity: Unknown
Chain: Iron Fish
Component: iron-fish/ironfish
Published: 2021-06-18
Source: https://github.com/iron-fish/ironfish/commit/b02253fc2cc6b2da4b6f650451e20de2ef39caa0
Type: security-commit

## Details
Reset crash fix by not autoseeding  (#226)

* Add confirmation to delete backup

Most people will delete this backup anyway, so provide confirmatiuon to
do it for the user.

* Reset crash fix by not autoseeding

We don't want to auto seed here so we dont crash when we are just trying
to pull accounts out of an old version.

## Patch
### ironfish-cli/src/commands/reset.ts
```diff
@@ -44,18 +44,22 @@ export default class Reset extends IronfishCommand {
 
     if (fs.existsSync(backupPath)) {
       this.log(`There is already an account backup at ${backupPath}`)
-      this.log(
-        `\nThat means this failed to run. Delete it manually, or move it somewhere and try again.`,
+
+      const confirmed = await cli.confirm(
+        `\nThis means this failed to run. Delete the accounts backup?\nAre you sure? (Y)es / (N)o`,
       )
-      this.exit(1)
+
+      if (!confirmed) this.exit(1)
+
+      fs.rmSync(backupPath)
     }
 
-    let node = await this.sdk.node()
+    let node = await this.sdk.node({ autoSeed: false })
 
     const confirmed =
       flags.confirm ||
       (await cli.confirm(
-        `You are about to destroy your node data at ${node.config.dataDir}\nAre you sure? (Y)es / (N)o`,
+        `\nYou are about to destroy your node data at ${node.config.dataDir}\nAre you sure? (Y)es / (N)o`,
       ))
 
     if (!confirmed) return
```
