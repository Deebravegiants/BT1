# [M] Insufficient permission checking in `Deno.makeTemp*` APIs

## Summary
Severity: Medium
Advisory: GHSA-hrqr-jv8w-v9jh
CVE: CVE-2024-27931
CWE: CWE-20
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:L/A:N (CVSS_V3)
Published: 2024-03-05
Source: https://github.com/advisories/GHSA-hrqr-jv8w-v9jh
Type: github-advisory

## Affected
- crates.io: `deno` — affected >=0 <1.41.1

## Details
### Impact

Insufficient validation of parameters in `Deno.makeTemp*` APIs would allow for creation of files outside of the allowed directories. This may allow the user to overwrite important files on the system that may affect other systems.

A user may provide a prefix or suffix to a `Deno.makeTemp*` API containing path traversal characters. The permission check would prompt for the base directory of the API, but the final file that was created would be outside of this directory:

```
$ mkdir /tmp/good
$ mkdir /tmp/bad
$ deno repl --allow-write=/tmp/good
> Deno.makeTempFileSync({ dir: "/tmp/bad" })
┌ ⚠️  Deno requests write access to "/tmp/bad".
├ Requested by `Deno.makeTempFile()` API.
├ Run again with --allow-write to bypass this prompt.
└ Allow? [y/n/A] (y = yes, allow; n = no, deny; A = allow all write permissions) > n
❌ Denied write access to "/tmp/bad".
Uncaught PermissionDenied: Requires write access to "/tmp/bad", run again with the --allow-write flag
    at Object.makeTempFileSync (ext:deno_fs/30_fs.js:176:10)
    at <anonymous>:1:27
> Deno.makeTempFileSync({ dir: "/tmp/good", prefix: "../bad/" })
"/tmp/good/../bad/a9432ef5"
$ ls -l /tmp/bad/a9432ef5
-rw-------@ 1 user  group  0 Mar  4 09:20 /tmp/bad/a9432ef5
```

### Patches

This is fixed in Deno 1.41.1.

## References
- https://github.com/denoland/deno/security/advisories/GHSA-hrqr-jv8w-v9jh
- https://nvd.nist.gov/vuln/detail/CVE-2024-27931
- https://github.com/denoland/deno
