# [?] reckless: fix crash on non-verbose output

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ElementsProject/lightning
Published: 2023-04-14
Source: https://github.com/ElementsProject/lightning/commit/6ac0842aa1709bd75d777cc7e5d074c35b804a33
Type: security-commit

## Details
reckless: fix crash on non-verbose output

Also cleans up verbose logic

## Patch
### tools/reckless
```diff
@@ -357,17 +357,11 @@ def _install_plugin(src: InstInfo) -> bool:
             url = f"{GITHUB_COM}" + src.repo.split("github.com")[-1]
         else:
             url = src.repo
-        # Ugly, but interactively handling stderr gets hairy.
-        if logging.root.level < logging.WARNING:
-            git = Popen(['git', 'clone', url, str(clone_path)],
-                        stdout=PIPE, stderr=PIPE)
-        else:
-            git = Popen(['git', 'clone', url, str(clone_path)],
-                        stdout=PIPE, stderr=PIPE)
+        git = Popen(['git', 'clone', url, str(clone_path)],
+                    stdout=PIPE, stderr=PIPE)
         git.wait()
         if git.returncode != 0:
-            if git.stderr:
-                print(git.stderr.read().decode())
+            logging.debug(git.stderr.read().decode())
             if Path(clone_path).exists():
                 remove_dir(clone_path)
             print('Error: Failed to clone repo')
@@ -406,7 +400,8 @@ def _install_plugin(src: InstInfo) -> bool:
             print('dependencies installed successfully')
         else:
             print('error encountered installing dependencies')
-            logging.debug(pip.stdout.read())
+            if pip.stdout:
+                logging.debug(pip.stdout.read())
             return False
     test = Popen([Path(plugin_path).joinpath(src.entry)], cwd=str(plugin_path),
                  stdout=PIPE, stderr=PIPE, text=True)
```
