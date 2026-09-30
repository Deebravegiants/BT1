# [?] Fix config:edit --remote crashing (#2612)

## Summary
Severity: Unknown
Chain: Iron Fish
Component: iron-fish/ironfish
Published: 2022-11-18
Source: https://github.com/iron-fish/ironfish/commit/2954fef2f4138f2a7ec5c37b198d0a208a680b15
Type: security-commit

## Details
Fix config:edit --remote crashing (#2612)

This would crash because the directory passed to mkdtempdir has a
slash so it thinks its 2 folders that don't exist.

## Patch
### ironfish-cli/src/commands/config/edit.ts
```diff
@@ -44,7 +44,7 @@ export class EditCommand extends IronfishCommand {
     const output = JSON.stringify(response.content, undefined, '   ')
 
     const tmpDir = os.tmpdir()
-    const folderPath = await mkdtempAsync(path.join(tmpDir, '@ironfish/sdk'))
+    const folderPath = await mkdtempAsync(path.join(tmpDir, '@ironfish-sdk-'))
     const filePath = path.join(folderPath, DEFAULT_CONFIG_NAME)
 
     await writeFileAsync(filePath, output)
```
