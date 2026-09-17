# [H] zeptoclaw has Android device shell blocklist bypass via argument permutation

## Summary
Severity: High
Advisory: GHSA-hhjv-jq77-cmvx
CWE: CWE-78
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-05
Source: https://github.com/advisories/GHSA-hhjv-jq77-cmvx
Type: github-advisory

## Affected
- crates.io: `zeptoclaw` — affected >=0 <0.6.2

## Details
### Summary
[zeptoclaw](https://github.com/qhkm/zeptoclaw) implements a [blocklist](https://github.com/qhkm/zeptoclaw/blob/fe2ef07cfec5bb46b42cdd65f52b9230c03e9270/src/tools/android/actions.rs#L413-L424) to prevent dangerous commands running in android device shell, but this blocklist has several blocked commands with argements in the pattern literal, such as `rm -f` and `rm -rf`, this can be simply bypassed by using different orders for these arguments, such as `rm -r -f` or `rm -fr` etc.

### Details
As in code [src/tools/android/actions.rs#L413-L424](https://github.com/qhkm/zeptoclaw/blob/fe2ef07cfec5bb46b42cdd65f52b9230c03e9270/src/tools/android/actions.rs#L413-L424), we can see the `rm -f` and `rm -rf` are hard coded and thus can be simply bypassed via `rm -r -f` or `rm -fr` etc.
```rust
pub async fn device_shell(adb: &AdbExecutor, cmd: &str) -> Result<String> {
    // Normalize whitespace for blocklist check
    let normalized: String = cmd.split_whitespace().collect::<Vec<_>>().join(" ");
    let lower = normalized.to_lowercase();

    let blocked = [
        "rm -rf",
        "rm -r",
        "reboot",
        "factory_reset",
        "wipe",
        "format",
        "dd if=",
        "mkfs",
        "flash",
        "fastboot",
    ];
    for pattern in &blocked {
        if lower.contains(pattern) {
            return Err(ZeptoError::Tool(format!(
                "Blocked dangerous command containing '{}'",
                pattern
            )));
        }
    }
```

### PoC
Set up [zeptoclaw](https://github.com/qhkm/zeptoclaw) with an Android tool and then run the command `rm -f -r` etc.

### Impact
Unauthorized command executed in Android device.

### Credit
[@zpbrent](https://github.com/zpbrent)

## References
- https://github.com/qhkm/zeptoclaw/security/advisories/GHSA-hhjv-jq77-cmvx
- https://github.com/qhkm/zeptoclaw/commit/68916c3e4f3af107f11940b27854fc7ef517058b
- https://github.com/qhkm/zeptoclaw
- https://github.com/qhkm/zeptoclaw/blob/fe2ef07cfec5bb46b42cdd65f52b9230c03e9270/src/tools/android/actions.rs#L413-L424
