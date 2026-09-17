# [H] jupyterlab-git has a command injection vulnerability in "Open Git Repository in Terminal"

## Summary
Severity: High
Advisory: GHSA-cj5w-8mjf-r5f8
CVE: CVE-2025-30370
CWE: CWE-78
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:C/C:L/I:H/A:H (CVSS_V3)
Published: 2025-04-04
Source: https://github.com/advisories/GHSA-cj5w-8mjf-r5f8
Type: github-advisory

## Affected
- PyPI: `jupyterlab-git` — affected >=0 <0.51.1

## Details
## Overview

On many platforms, a third party can create a Git repository under a name that includes a shell command substitution [^1] string in the syntax `$(<command>)`. These directory names are allowed in macOS and a majority of Linux distributions [^2]. If a user starts `jupyter-lab` in a parent directory of this inappropriately-named Git repository, opens it, and clicks "Git > Open Git Repository in Terminal" from the menu bar, then the injected command `<command>` is run in the user's shell without the user's permission.

This issue is occurring because when that menu entry is clicked, `jupyterlab-git` opens the terminal and runs `cd <git-repo-path>` through the shell to set the current directory [^3]. Doing so runs any command substitution strings present in the directory name, which leads to the command injection issue described here. A previous patch provided an incomplete fix [^4].

[^1]: https://www.gnu.org/software/bash/manual/html_node/Command-Substitution.html
[^2]: https://www.gnu.org/software/libc/manual/html_node/File-Name-Portability.html
[^3]: https://github.com/jupyterlab/jupyterlab-git/blob/7eb3b06f0092223bd5494688ec264527bbeb2195/src/commandsAndMenu.tsx#L175-L184
[^4]: https://github.com/jupyterlab/jupyterlab-git/pull/1196
 

## Scope of Impact

This issue allows for arbitrary code execution via command injection. A wide range of actions are permitted by this issue, including but not limited to: modifying files, exfiltrating data, halting services, or compromising the server's security rules.

We have scanned the source code of `jupyterlab-git` for other command injection risks, and have not found any at the time of writing.

This issue was reproduced on the latest release of `jupyterlab-git`, v0.51.0. The steps taken to reproduce this issue are described in the "Proof-of-concept" section below.
 

## Proof-of-concept

1. Create a new directory via `mkdir test/ && cd test/`.

2. Create a new Git repository under `test/` with a command substitution string in the directory name by running these commands:

```
mkdir '$(touch pwned.txt)'
cd '$(touch pwned.txt)/'
git init
cd ..
```

3. Start JupyterLab from `test/` by running jupyter lab.
4. With JupyterLab open in the browser, double click on `$(touch pwned.txt)` in the file browser.
5. From the top menu bar, click "Git > Open Git Repository in Terminal".
6. Verify that `pwned.txt` is created under `test/`. This demonstrates the command injection issue described here.

## Proof-of-concept mitigation

The issue can be mitigated by the patch shown below.

<details><summary>Patch (click to expand)</summary>

```diff
diff --git a/src/commandsAndMenu.tsx b/src/commandsAndMenu.tsx
index 3779a6c..71ddcea 100644
--- a/src/commandsAndMenu.tsx
+++ b/src/commandsAndMenu.tsx
@@ -164,31 +164,13 @@ export function addCommands(
     label: trans.__('Open Git Repository in Terminal'),
     caption: trans.__('Open a New Terminal to the Git Repository'),
     execute: async args => {
-      const main = (await commands.execute(
-        'terminal:create-new',
-        args
-      )) as MainAreaWidget<ITerminal.ITerminal>;
+      const cwd = gitModel.pathRepository;
+      const main = (await commands.execute('terminal:create-new', {
+        ...args,
+        cwd
+      })) as MainAreaWidget<ITerminal.ITerminal>;
 
-      try {
-        if (gitModel.pathRepository !== null) {
-          const terminal = main.content;
-          terminal.session.send({
-            type: 'stdin',
-            content: [
-              `cd "${gitModel.pathRepository
-                .split('"')
-                .join('\\"')
-                .split('`')
-                .join('\\`')}"\n`
-            ]
-          });
-        }
-
-        return main;
-      } catch (e) {
-        console.error(e);
-        main.dispose();
-      }
+      return main;
```
</details>

This patch removes the `cd <git-repo-path>` shell command that causes the issue. To preserve the existing behavior, the `cwd` argument is set to `<git-repo-path>` when a terminal session is created via the `terminal:create-new` JupyterLab command. This preserves the existing application behavior while mitigating the command injection issue.

We have verified that this patch works when applied to a local installation of `jupyterlab-git`. We have also verified that the `cwd` argument is available in all versions of JupyterLab 4, so this patch should be fully backwards-compatible.

## Workarounds

We recommend that users upgrade to the patched versions listed on this GHSA. However, if a user is unable to upgrade, there are 3 different ways to mitigate this vulnerability without upgrading to a patch. 

1. Disable terminals on `jupyter-server` level:
    ```
    c.ServerApp.terminals_enabled =  False
    ```

2. Disable the terminals server extension:
    ```
    jupyter server extension disable jupyter_server_terminals
    ```

3. Disable the lab extension:
    ```
    jupyter labextension disable @jupyterlab/terminal-extension
    ```

## References
- https://github.com/jupyterlab/jupyterlab-git/security/advisories/GHSA-cj5w-8mjf-r5f8
- https://nvd.nist.gov/vuln/detail/CVE-2025-30370
- https://github.com/jupyterlab/jupyterlab-git/pull/1196
- https://github.com/jupyterlab/jupyterlab-git/commit/b46482993f76d3a546015c6a94ebed8b77fc2376
- https://github.com/jupyterlab/jupyterlab-git
- https://github.com/jupyterlab/jupyterlab-git/blob/7eb3b06f0092223bd5494688ec264527bbeb2195/src/commandsAndMenu.tsx#L175-L184
