# [C] Improper Scope Validation in the `open` Endpoint of `tauri-plugin-shell`

## Summary
Severity: Critical
Advisory: GHSA-c9pr-q8gx-3mgp
CVE: CVE-2025-31477
CWE: CWE-20
Ecosystem: crates.io, npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-04-02
Source: https://github.com/advisories/GHSA-c9pr-q8gx-3mgp
Type: github-advisory

## Affected
- crates.io: `tauri-plugin-shell` — affected >=0 <2.2.1
- npm: `@tauri-apps/plugin-shell` — affected >=0 <2.2.1

## Details
### Impact

The Tauri [`shell`](https://tauri.app/plugin/shell/)  plugin exposes functionality to execute code and open programs on the system. The [`open`](https://tauri.app/reference/javascript/shell/#open) endpoint of this plugin is designed to allow open functionality with the system opener (e.g. 
 `xdg-open` on Linux). This was meant to be restricted to a reasonable number of protocols like `https` or `mailto` by default.

This default restriction was not functional due to improper validation of the allowed protocols, allowing for potentially dangerous protocols like `file://`, `smb://`, or `nfs://` and others  to be opened by the system registered protocol handler.

By passing untrusted user input to the `open` endpoint these potentially dangerous protocols can be abused to gain remote code execution on the system. This either requires direct exposure of the endpoint to application users or code execution in the frontend of a Tauri application.

You are not affected if you have explicitly configured a validation regex or manually set the `open` endpoint to `true` in the plugin configuration. 

Technically the scope was never a limitation for the rust side as it is not seen as an enforceable security boundary but we decided to mark the rust crate as affected since the plugin does not need to be a frontend dependency to be exposed.

### Patches

The issue has been patched in the `2.2.1` version of the plugin.
The plugin now differentiates between an unset scope and an explicit validation disable for the `open` endpoint.

### Workarounds 

A way to prevent arbitrary protocols would be setting the shell plugin configuration value `open` to `true`.

`tauri.conf.json`
```json5 
"plugins": {
    "shell": {
          "open": true
     },
}
```

The above will only allow `mailto`, `http` and `https` links to be opened.

If the `open` endpoint should not be allowed at all there are two possible workarounds.
- Defining a non matching regex like `tauri^` in the plugin configuration
- Removing `shell:default` and all instances of `shell:allow-open` from the [`capabilities`](https://tauri.app/security/capabilities/) 

Alternatively we recommend usage of the [`opener`](https://tauri.app/plugin/opener/)  plugin, as the shell plugin deprecated the `open` endpoint previously.
### References

#### PoC

This is a windows specific proof of concept.

1. Use `create-tauri-app` to make a new Tauri app.
2. Run `tauri add shell` to add the shell plugin.
3. Execute `await window.__TAURI_INTERNALS__.invoke("plugin:shell|open", {path: "file:///c:/windows/system32/calc.exe"});` in the developer console.
4. Observe the calculator being executed

## References
- https://github.com/tauri-apps/plugins-workspace/security/advisories/GHSA-c9pr-q8gx-3mgp
- https://nvd.nist.gov/vuln/detail/CVE-2025-31477
- https://github.com/tauri-apps/plugins-workspace/commit/9cf0390a52497e273db1a1b613a0e26827aa327c
- https://github.com/tauri-apps/plugins-workspace
