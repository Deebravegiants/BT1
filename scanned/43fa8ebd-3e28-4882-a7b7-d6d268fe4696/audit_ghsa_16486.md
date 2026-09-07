# [M] iFrames Bypass Origin Checks for Tauri API Access Control

## Summary
Severity: Medium
Advisory: GHSA-57fm-592m-34r7
CVE: CVE-2024-35222
CWE: CWE-284
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2024-05-23
Source: https://github.com/advisories/GHSA-57fm-592m-34r7
Type: github-advisory

## Affected
- crates.io: `tauri` — affected >=0 <1.6.7
- crates.io: `tauri` — affected >=2.0.0-beta.0 <2.0.0-beta.20

## Details
## Impact

Remote origin iFrames in Tauri applications can access the Tauri IPC endpoints without being explicitly allowed in the [`dangerousRemoteDomainIpcAccess`](https://v1.tauri.app/api/config/#securityconfig.dangerousremotedomainipcaccess) in v1 and in the [`capabilities`](https://v2.tauri.app/security/capabilities/#remote-api-access) in v2.
This bypasses the origin check and allows iFrames to access the IPC endpoints exposed to the parent window.

For this to be exploitable, an attacker must have script execution (e.g. XSS) in a script-enabled iFrame of a Tauri application.

## Patches

The patches include changes to wry and the behaviour of Tauri applications using iFrames. Previously, we injected the Tauri IPC initialization script into iFrames on MacOS, which was unintended. This is now also disabled to be consistent with all other supported operating systems.

This means that the Tauri invoke functionality is no longer accessible from iFrames, except on Windows when the origin of the Tauri window and the origin of the iFrame are the same.

We have also added a new protection mechanism to the IPC layer to protect against iFrames directly using the WebView IPC functionality (e.g. via `window.ipc.postMessage`).
This introduces an invoke key (`__TAURI_INVOKE_KEY__`) which is used to prevent frames that have not been initialized by the Tauri core from sending messages to the Tauri IPC.
This key is **not** used to protect against compromised Tauri windows or WebViews and is **only** intended to block IPC access from sub-frames.

Unauthorized messages to the Tauri IPC from an iFrame or other non-initialized context will log a warning and the potentially malicious IPC call will be ignored.

## Workarounds

These workarounds should only be considered if you are unable to upgrade to the patched Tauri version in time.

As a workaround for v1 Tauri applications, we recommend using a dedicated window for untrusted origins instead of iFrames, or disabling script execution within the iFrame.

For v2 Tauri applications targeting Linux, it is possible to use either a dedicated window or [multiple WebViews](https://github.com/tauri-apps/tauri/tree/dev/examples/multiwebview) in the main window to simulate iFrame behavior.
On other platforms, it is only possible to use dedicated windows or disable script execution inside the iFrame, as described for v1.

## References

If you have any questions or comments about this advisory:

Open an issue in tauri or
Email us at [security@tauri.app](mailto:security@tauri.app)

The original submissions from the reporter:

> ### Context
> 
> This is following up on the comments here: https://github.com/tauri-apps/tauri/issues/8316, and here: https://discord.com/channels/616186924390023171/1227969106091966475. I was asked to submit my findings as a vulnerability report.
> 
> Firstly, thank you to all of you from the core team that helped out and guided me through understanding this issue! Huge fan of Tauri, and I'm excited to see it succeed!
> 
> ### Summary
> 
> In short, **any iframe you add in your Tauri frontend will get access to Tauri APIs, even in isolation mode**.
> 
> Any embedded iframe that you don't own will be able to invoke the same APIs your app does. While isolation mode allows for finer grained control of what Tauri APIs can be called, it is not possible to determine if a request is coming your own app, or from a potentially malicious iframe.
> 
> This means your app could be open to malicious iframe being able to execute any command your app can, and there doesn't seem to be a mechanism to filter these out.
> 
> ### Details
> 
> I'm not an expert in Tauri source code, so I can't be sure I'm on the right track here, but I assume this has to do with how the webview is bootstrapped with the Tauri APIs.
> 
> I know there's various handlers that get set, such as opening `target="_blank"` links via a shell command, and of course setting `invoke` and other such APIs. Sounds like the issue is somewhere there and the APIs are being injected where they shouldn't.
> 
> Technically it seems that an attacker couldn't actually receive a response from the command it executes. Tauri IPC can't route the response back to the invoking iframe, but the action is still executed, with the response just being dropped. You see these messages in the logs:
> 
> ```
> [Warning] [TAURI] Couldn't find callback id 3399436348 in window. This happens when the app is reloaded while Rust is running an asynchronous operation.
> ```
> 
> ### PoC
> 
> Repository with reproduction steps: https://github.com/begleynk/tauri-sandbox-iframe-escape-poc
> 
> Building on that POC, here is a video of a Codepen iframe running inside an isolation mode Tauri app, invoking the same "Greet" command the frontend is invoking.
> 
> https://github.com/tauri-apps/tauri/assets/1065208/8efd5f9d-3116-4068-b98b-6ace7de9261c
> 
> This is done with the following code running inside Codepen:
> 
> ```javascript
> window.__TAURI_INVOKE__("greet", { name: "From CodePen" })
> ```
> 
> ### Impact
> 
> Valid commands with potentially unwanted consequences ("delete project", "transfer credits", etc.) could be invoked by an attacker that controls the content of an iframe running inside a Tauri app.

## References
- https://github.com/tauri-apps/tauri/security/advisories/GHSA-57fm-592m-34r7
- https://nvd.nist.gov/vuln/detail/CVE-2024-35222
- https://github.com/tauri-apps/tauri/issues/8316
- https://github.com/tauri-apps/tauri/commit/d950ac1239817d17324c035e5c4769ee71fc197d
- https://github.com/tauri-apps/tauri/commit/f6d81dfe0871e0ccd012e5190d41e3767e733608
- https://github.com/tauri-apps/tauri
