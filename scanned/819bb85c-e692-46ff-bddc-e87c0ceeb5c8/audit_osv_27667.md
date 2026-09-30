# [C] Rusts's `std::process::Command` did not properly escape arguments of batch files on Windows

## Summary
Severity: Critical
Advisory: CVE-2024-24576
Aliases: GHSA-q455-m56c-85mh
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-04-09
Source: https://osv.dev/vulnerability/CVE-2024-24576
Type: osv

## Details
Rust is a programming language. The Rust Security Response WG was notified that the Rust standard library prior to version 1.77.2 did not properly escape arguments when invoking batch files (with the `bat` and `cmd` extensions) on Windows using the `Command`. An attacker able to control the arguments passed to the spawned process could execute arbitrary shell commands by bypassing the escaping. The severity of this vulnerability is critical for those who invoke batch files on Windows with untrusted arguments. No other platform or use is affected.

The `Command::arg` and `Command::args` APIs state in their documentation that the arguments will be passed to the spawned process as-is, regardless of the content of the arguments, and will not be evaluated by a shell. This means it should be safe to pass untrusted input as an argument.

On Windows, the implementation of this is more complex than other platforms, because the Windows API only provides a single string containing all the arguments to the spawned process, and it's up to the spawned process to split them. Most programs use the standard C run-time argv, which in practice results in a mostly consistent way arguments are splitted.

One exception though is `cmd.exe` (used among other things to execute batch files), which has its own argument splitting logic. That forces the standard library to implement custom escaping for arguments passed to batch files. Unfortunately it was reported that our escaping logic was not thorough enough, and it was possible to pass malicious arguments that would result in arbitrary shell execution.

Due to the complexity of `cmd.exe`, we didn't identify a solution that would correctly escape arguments in all cases. To maintain our API guarantees, we improved the robustness of the escaping code, and changed the `Command` API to return an `InvalidInput` error when it cannot safely escape an argument. This error will be emitted when spawning the process.

The fix is included in Rust 1.77.2. Note that the new escaping logic for batch files errs on the conservative side, and could reject valid arguments. Those who implement the escaping themselves or only handle trusted inputs on Windows can also use the `CommandExt::raw_arg` method to bypass the standard library's escaping logic.

## References
- http://www.openwall.com/lists/oss-security/2024/04/09/16
- https://doc.rust-lang.org/std/io/enum.ErrorKind.html#variant.InvalidInput
- https://doc.rust-lang.org/std/os/windows/process/trait.CommandExt.html#tymethod.raw_arg
- https://doc.rust-lang.org/std/process/struct.Command.html
- https://doc.rust-lang.org/std/process/struct.Command.html#method.arg
- https://doc.rust-lang.org/std/process/struct.Command.html#method.args
- https://github.com/rust-lang/rust/issues
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/N323QAEEUVTJ354BTVQ7UB6LYXUX2BCL/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/RPH3PF7DVSS2LVIRLW254VWUPVKJN46P/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/W7WRFOIAZXYUPGXGR5UEEW7VTTOD4SZ3/
- https://www.kb.cert.org/vuls/id/123335
- https://www.rust-lang.org/policies/security
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/24xxx/CVE-2024-24576.json
- https://github.com/rust-lang/rust/security/advisories/GHSA-q455-m56c-85mh
- https://nvd.nist.gov/vuln/detail/CVE-2024-24576
