# [M] Environment variables still accessible through /proc

## Summary
Severity: Medium
Advisory: GHSA-wj7f-468m-6mv8
CWE: CWE-200
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-12-01
Source: https://github.com/advisories/GHSA-wj7f-468m-6mv8
Type: github-advisory

## Affected
- crates.io: `birdcage` — affected >=0 <0.7.0

## Details
### Impact

Environment variables can be read from procfs unless a new process is started.

### PoC

```
use birdcage::{Birdcage, Sandbox};
use std::{env, fs};

fn main() {
    Birdcage::new().lock().unwrap();

    assert_eq!(env::var_os("SECRET"), None);

    let environ = fs::read_to_string("/proc/self/environ").unwrap();
    assert!(!environ.contains("SECRET"), "ENVIRON CONTAINS SECRET:\n{environ}");
}
```

```
$  SECRET=test cargo run
thread 'main' panicked at src/main.rs:10:5:
ENVIRON CONTAINS SECRET:
 [truncated]
 ```

### Possible Solutions

The simplest solution would be relying on the ptrace isolation and **always** spawning a new process by changing birdcage's API to create a new command. With an additional PID namespace the guarantees could be even further reinforced.

## References
- https://github.com/phylum-dev/birdcage/security/advisories/GHSA-wj7f-468m-6mv8
- https://github.com/phylum-dev/birdcage
