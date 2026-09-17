# [H] Deno arbitrary file descriptor close via `op_node_ipc_pipe()` leading to permission prompt bypass

## Summary
Severity: High
Advisory: GHSA-6q4w-9x56-rmwq
CVE: CVE-2024-27933
CWE: CWE-863
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-03-06
Source: https://github.com/advisories/GHSA-6q4w-9x56-rmwq
Type: github-advisory

## Affected
- crates.io: `deno` — affected >=1.39.0 <1.39.1

## Details
### Summary

Use of raw file descriptors in `op_node_ipc_pipe()` leads to premature close of arbitrary file descriptors, allowing standard input to be re-opened as a different resource resulting in permission prompt bypass.


### Details

Node child_process IPC relies on the JS side to pass the raw IPC file descriptor to `op_node_ipc_pipe()`, which returns a `IpcJsonStreamResource` ID associated with the file descriptor. On closing the resource, the raw file descriptor is closed together.

Although closing a file descriptor is seemingly a harmless task, this has been known to be exploitable:
- With `--allow-read` and `--allow-write` permissions, one can open `/dev/ptmx` as stdin. This device happily accepts TTY ioctls and pipes anything written into it back to the reader. 
  - This has been presented in a hacking competition (WACON 2023 Quals "dino jail").
  - However, the precondition of this challenge was heavily contrived: fd 0 has manually been closed by FFI and `setuid()` was used to drop permissions and deny access to `/proc` since global write permissions are usually equivalent to arbitrary code execution (`/proc/self/mem`).

As this vulnerability conveniently allows us to close stdin (fd 0) without any FFI, we can open any resource that when read returns `y`, `Y` or `A` as its first character ([runtimes/permissions/prompter.rs](https://github.com/denoland/deno/blob/v1.39.0/runtime/permissions/prompter.rs#L265)) to bypass the prompt.

There is a caveat however - all stdio/stdin/stderr streams are [locked](https://github.com/denoland/deno/blob/v1.39.0/runtime/permissions/prompter.rs#L214), after which [`clear_stdin()`](https://github.com/denoland/deno/blob/v1.39.0/runtime/permissions/prompter.rs#L220) is called. This invokes [`libc::tcflush(0, libc::TCIFLUSH)`](https://github.com/denoland/deno/blob/v1.39.0/runtime/permissions/prompter.rs#L99) which fails on a non-TTY file descriptor.

This can be exploited by widening the race window between `clear_stdin()` and the next [`stdin_lock.read_line()`](https://github.com/denoland/deno/blob/v1.39.0/runtime/permissions/prompter.rs#L256). Notably, the prompt message contains the requested resource name (path) which is filtered by [`strip_ansi_codes_and_ascii_control()`](https://github.com/denoland/deno/blob/v1.39.0/runtime/permissions/prompter.rs#L225). This is also concatenated by [`write!()`](https://github.com/denoland/deno/blob/v1.39.0/runtime/permissions/prompter.rs#L241) to make a single buffer printed out to stderr. Thus, if we request a very long resource name, the window will widen allowing us to easily and stably race another Worker that closes fd 0 and opens a resource starting with an `A\n` within the race window.

Note that attacker does not need any permissions to exploit this bug to a full permission prompt bypass, as Cache API can be used to create and open files with controlled content without any permissions. Refer to the Impact section for more details.


### PoC

Testing environment is Docker image `denoland/deno:alpine-1.39.0@sha256:95064390f2c115673762bfc4fe15b1a7f81c859038b8c02b277ede7cd8a2ccbf`.

Below PoC closes stdout (fd 1) and then prints two lines, one on stdout and one on stderr. Only the latter line is shown as stdout file descriptor is closed.

```js
const ops = Deno[Deno.internal].core.ops;

// open fd 1 as ipc stream resource
const rid = ops.op_node_ipc_pipe(1);

// close resource & fd 1
Deno.close(rid);

// this should not be seen (stdout)
console.log('not seen');

// but this is seen (stderr)
console.error('seen');
```

Below is `/proc/$(pgrep deno)/fd` right after executing the last line of the above PoC. We see that fd 1 is indeed missing.

```text
total 0
dr-x------ 2 root root 30 Dec 18 07:07 ./
dr-xr-xr-x 9 root root  0 Dec 18 07:07 ../
lrwx------ 1 root root 64 Dec 18 07:07 0 -> /dev/pts/0
l-wx------ 1 root root 64 Dec 18 07:07 10 -> 'pipe:[159305]'
lr-x------ 1 root root 64 Dec 18 07:07 11 -> 'pipe:[159306]'
l-wx------ 1 root root 64 Dec 18 07:07 12 -> 'pipe:[159306]'
lrwx------ 1 root root 64 Dec 18 07:07 13 -> /deno-dir/dep_analysis_cache_v1
l-wx------ 1 root root 64 Dec 18 07:07 14 -> 'pipe:[159305]'
l-wx------ 1 root root 64 Dec 18 07:07 15 -> 'pipe:[159306]'
lrwx------ 1 root root 64 Dec 18 07:07 16 -> /deno-dir/node_analysis_cache_v1
lrwx------ 1 root root 64 Dec 18 07:07 17 -> /dev/pts/0
lrwx------ 1 root root 64 Dec 18 07:07 18 -> /dev/pts/0
lrwx------ 1 root root 64 Dec 18 07:07 19 -> /dev/pts/0
lrwx------ 1 root root 64 Dec 18 07:07 2 -> /dev/pts/0
lrwx------ 1 root root 64 Dec 18 07:07 20 -> 'anon_inode:[eventpoll]'
lrwx------ 1 root root 64 Dec 18 07:07 21 -> 'anon_inode:[eventfd]'
lrwx------ 1 root root 64 Dec 18 07:07 22 -> 'anon_inode:[eventpoll]'
lrwx------ 1 root root 64 Dec 18 07:07 23 -> 'socket:[159302]'
lrwx------ 1 root root 64 Dec 18 07:07 24 -> 'anon_inode:[eventpoll]'
lrwx------ 1 root root 64 Dec 18 07:07 25 -> 'anon_inode:[eventfd]'
lrwx------ 1 root root 64 Dec 18 07:07 26 -> 'anon_inode:[eventpoll]'
lrwx------ 1 root root 64 Dec 18 07:07 27 -> 'socket:[159302]'
lrwx------ 1 root root 64 Dec 18 07:07 28 -> 'socket:[159310]'
lrwx------ 1 root root 64 Dec 18 07:07 29 -> 'socket:[159308]'
lrwx------ 1 root root 64 Dec 18 07:07 3 -> 'anon_inode:[eventpoll]'
lrwx------ 1 root root 64 Dec 18 07:07 30 -> 'socket:[159309]'
lrwx------ 1 root root 64 Dec 18 07:07 4 -> 'anon_inode:[eventfd]'
lrwx------ 1 root root 64 Dec 18 07:07 5 -> 'anon_inode:[eventpoll]'
lrwx------ 1 root root 64 Dec 18 07:07 6 -> 'socket:[159302]'
lrwx------ 1 root root 64 Dec 18 07:07 7 -> 'socket:[159303]'
lrwx------ 1 root root 64 Dec 18 07:07 8 -> 'socket:[159302]'
lr-x------ 1 root root 64 Dec 18 07:07 9 -> 'pipe:[159305]'
```


### Impact

Use of raw file descriptors in `op_node_ipc_pipe()` leads to premature close of arbitrary file descriptors. This allow standard input (fd 0) to be closed and re-opened for a different resource, which allows a silent permission prompt bypass. This is exploitable by an attacker controlling the code executed inside a Deno runtime to obtain arbitrary code execution on the host machine regardless of permissions.

This bug is **known to be exploitable** - there is a working exploit that achieves arbitrary code execution by bypassing prompts from zero permissions, additionally abusing the fact that Cache API lacks filesystem permission checks. The attack can be conducted silently as stderr can also be closed, suppressing all prompt outputs.

> Note that Deno's security model is currently described as follows:
> - All runtime I/O is considered to be privileged and must always be guarded by a runtime permission. This includes filesystem access, network access, etc.
>   - The only exception to this is runtime storage explosion attacks that are isolated to a part of the file system, caused by evaluated code (for example, caching big dependencies or no limits on runtime caches such as the Web Cache API).
>
> Although it is ambiguous if the fundamental lack of file system permission checks on Web Cache API is a vulnerability or not, the reporter have not reported this as a vulnerability assuming that this is a known risk (or a feature).

Affected version of Deno is 1.39.0.

- Introduced with commit 5a91a06
- Fixed with commit 55fac9f

## References
- https://github.com/denoland/deno/security/advisories/GHSA-6q4w-9x56-rmwq
- https://nvd.nist.gov/vuln/detail/CVE-2024-27933
- https://github.com/denoland/deno/commit/55fac9f5ead6d30996400e8597c969b675c5a22b
- https://github.com/denoland/deno/commit/5a91a065b882215dde209baf626247e54c21a392
- https://github.com/denoland/deno
- https://github.com/denoland/deno/blob/v1.39.0/runtime/permissions/prompter.rs#L214
- https://github.com/denoland/deno/blob/v1.39.0/runtime/permissions/prompter.rs#L220
- https://github.com/denoland/deno/blob/v1.39.0/runtime/permissions/prompter.rs#L225
- https://github.com/denoland/deno/blob/v1.39.0/runtime/permissions/prompter.rs#L241
- https://github.com/denoland/deno/blob/v1.39.0/runtime/permissions/prompter.rs#L256
- https://github.com/denoland/deno/blob/v1.39.0/runtime/permissions/prompter.rs#L265
- https://github.com/denoland/deno/blob/v1.39.0/runtime/permissions/prompter.rs#L99
