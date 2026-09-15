# [M] gitoxide does not detect SHA-1 collision attacks

## Summary
Severity: Medium
Advisory: GHSA-2frx-2596-x5r6
CVE: CVE-2025-31130
CWE: CWE-328
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2025-04-04
Source: https://github.com/advisories/GHSA-2frx-2596-x5r6
Type: github-advisory

## Affected
- crates.io: `gix-features` — affected >=0 <0.41.0
- crates.io: `gix-commitgraph` — affected >=0 <0.27.0
- crates.io: `gix-index` — affected >=0 <0.39.0
- crates.io: `gix-object` — affected >=0 <0.48.0
- crates.io: `gix-odb` — affected >=0 <0.68.0
- crates.io: `gix-pack` — affected >=0 <0.58.0
- crates.io: `gitoxide` — affected >=0 <0.42.0
- crates.io: `gitoxide-core` — affected >=0 <0.46.0
- crates.io: `gix` — affected >=0 <0.71.0
- crates.io: `gix-archive` — affected >=0 <0.20.0
- crates.io: `gix-blame` — affected >=0 <0.1.0
- crates.io: `gix-config` — affected >=0 <0.44.0
- crates.io: `gix-diff` — affected >=0 <0.51.0
- crates.io: `gix-dir` — affected >=0 <0.13.0
- crates.io: `gix-discover` — affected >=0 <0.39.0
- crates.io: `gix-filter` — affected >=0 <0.18.0
- crates.io: `gix-fsck` — affected >=0 <0.10.0
- crates.io: `gix-merge` — affected >=0 <0.4.0
- crates.io: `gix-negotiate` — affected >=0 <0.19.0
- crates.io: `gix-protocol` — affected >=0 <0.49.0
- crates.io: `gix-ref` — affected >=0 <0.51.0
- crates.io: `gix-revision` — affected >=0 <0.33.0
- crates.io: `gix-revwalk` — affected >=0 <0.19.0
- crates.io: `gix-status` — affected >=0 <0.18.0
- crates.io: `gix-traverse` — affected >=0 <0.45.0
- crates.io: `gix-worktree` — affected >=0 <0.40.0
- crates.io: `gix-worktree-state` — affected >=0 <0.18.0

## Details
### Summary
gitoxide uses SHA-1 hash implementations without any collision detection, leaving it vulnerable to hash collision attacks.

### Details
gitoxide uses the `sha1_smol` or `sha1` crate, both of which implement standard SHA-1 without any mitigations for collision attacks. This means that two distinct Git objects with colliding SHA-1 hashes would break the Git object model and integrity checks when used with gitoxide.

The SHA-1 function is considered cryptographically insecure. However, in the wake of the SHAttered attacks, this issue was mitigated in Git 2.13.0 in 2017 by using the [sha1collisiondetection](https://github.com/crmarcstevens/sha1collisiondetection) algorithm by default and producing an error when known SHA-1 collisions are detected. Git is in the process of migrating to using SHA-256 for object hashes, but this has not been rolled out widely yet and gitoxide does not support SHA-256 object hashes.

### PoC
The following program demonstrates the problem, using the two [SHAttered PDFs](https://shattered.io/):

```rust
use sha1_checked::{CollisionResult, Digest};

fn sha1_oid_of_file(filename: &str) -> gix::ObjectId {
    let mut hasher = gix::features::hash::hasher(gix::hash::Kind::Sha1);
    hasher.update(&std::fs::read(filename).unwrap());
    gix::ObjectId::Sha1(hasher.digest())
}

fn sha1dc_oid_of_file(filename: &str) -> Result<gix::ObjectId, String> {
    // Matches Git’s behaviour.
    let mut hasher = sha1_checked::Builder::default().safe_hash(false).build();
    hasher.update(&std::fs::read(filename).unwrap());
    match hasher.try_finalize() {
        CollisionResult::Ok(digest) => Ok(gix::ObjectId::Sha1(digest.into())),
        CollisionResult::Mitigated(_) => unreachable!(),
        CollisionResult::Collision(digest) => Err(format!(
            "Collision attack: {}",
            gix::ObjectId::Sha1(digest.into()).to_hex()
        )),
    }
}

fn main() {
    dbg!(sha1_oid_of_file("shattered-1.pdf"));
    dbg!(sha1_oid_of_file("shattered-2.pdf"));
    dbg!(sha1dc_oid_of_file("shattered-1.pdf"));
    dbg!(sha1dc_oid_of_file("shattered-2.pdf"));
}
```

The output is as follows:

```
[src/main.rs:24:5] sha1_oid_of_file("shattered-1.pdf") = Sha1(38762cf7f55934b34d179ae6a4c80cadccbb7f0a)
[src/main.rs:25:5] sha1_oid_of_file("shattered-2.pdf") = Sha1(38762cf7f55934b34d179ae6a4c80cadccbb7f0a)
[src/main.rs:26:5] sha1dc_oid_of_file("shattered-1.pdf") = Err(
    "Collision attack: 38762cf7f55934b34d179ae6a4c80cadccbb7f0a",
)
[src/main.rs:27:5] sha1dc_oid_of_file("shattered-2.pdf") = Err(
    "Collision attack: 38762cf7f55934b34d179ae6a4c80cadccbb7f0a",
)
```

The latter behaviour matches Git.

Since the SHAttered PDFs are not in a valid format for Git objects, a direct proof‐of‐concept using higher‐level APIs cannot be immediately demonstrated without significant computational resources.

### Impact
An attacker with the ability to mount a collision attack on SHA-1 like the [SHAttered](https://shattered.io/) or [SHA-1 is a Shambles](https://sha-mbles.github.io/) attacks could create two distinct Git objects with the same hash. This is becoming increasingly affordable for well‐resourced attackers, with the Shambles researchers in 2020 estimating $45k for a chosen‐prefix collision or $11k for a classical collision, and projecting less than $10k for a chosen‐prefix collision by 2025. The result could be used to disguise malicious repository contents, or potentially exploit assumptions in the logic of programs using gitoxide to cause further vulnerabilities.

This vulnerability affects any user of gitoxide, including `gix-*` library crates, that reads or writes Git objects.

## References
- https://github.com/GitoxideLabs/gitoxide/security/advisories/GHSA-2frx-2596-x5r6
- https://nvd.nist.gov/vuln/detail/CVE-2025-31130
- https://github.com/GitoxideLabs/gitoxide/commit/f253f02a6658b3b7612a50d56c71f5ae4da4ca21
- https://github.com/GitoxideLabs/gitoxide
- https://rustsec.org/advisories/RUSTSEC-2025-0021.html
