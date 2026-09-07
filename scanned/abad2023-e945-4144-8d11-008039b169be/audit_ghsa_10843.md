# [M] sbt: Source dependency feature (via crafted VCS URL) leads to arbitrary code execution on Windows

## Summary
Severity: Medium
Advisory: GHSA-x4ff-q6h8-v7gw
CVE: CVE-2026-32948
CWE: CWE-78
Ecosystem: Maven
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-24
Source: https://github.com/advisories/GHSA-x4ff-q6h8-v7gw
Type: github-advisory

## Affected
- Maven: `org.scala-sbt:sbt` — affected >=0.9.5 <1.12.8

## Details
### Summary
On Windows, sbt uses `Process("cmd", "/c", ...)` to run VCS commands (git, hg, svn). The URI fragment (branch, tag, revision) is user-controlled via the build definition and passed to these commands without validation. Because `cmd /c` interprets `&`, `|`, and `;` as command separators, a malicious fragment can execute arbitrary commands.

### Patched version

Technically, sbt 1.12.7 is patched, but it has a bug that makes source dependency non-functional, so update to **sbt 1.12.8** or later instead.

### Details
- [Resolvers.scala L84–95](https://github.com/sbt/sbt/blob/dc90f160dfb563f46fd1a7b97945c381d15e2a6c/main/src/main/scala/sbt/Resolvers.scala#L84-L95) — git resolver passes `uri.getFragment()` to `run()` without sanitization
- [Resolvers.scala L137–145](https://github.com/sbt/sbt/blob/dc90f160dfb563f46fd1a7b97945c381d15e2a6c/main/src/main/scala/sbt/Resolvers.scala#L137-L145) — `run()` uses `Process("cmd", "/c", ...)` on Windows, so `cmd` interprets `&&` as command separator

### PoC
```sh
# build.properties
# sbt.version=1.12.5  # Tested on those two versions of sbt
sbt.version=2.0.0-RC9
```

```scala
// build.sbt

ThisBuild / scalaVersion := "2.12.19"

lazy val root = project
  .in(file("."))
  .dependsOn(vulnerable)

lazy val vulnerable = RootProject(
  uri("https://github.com/sbt/io.git#develop%26%26calc.exe")
)
```

### Impact

Windows users are impacted. An attacker can execute arbitrary Windows commands if they control the dependency URI.

## References
- https://github.com/sbt/sbt/security/advisories/GHSA-x4ff-q6h8-v7gw
- https://nvd.nist.gov/vuln/detail/CVE-2026-32948
- https://github.com/sbt/sbt/commit/1ce945b6b79cbe3cef6c0fe9efbbd2904e0f479e
- https://github.com/sbt/sbt/commit/3a474ab060df4dbfa825a7e7bc97e00056519800
- https://github.com/sbt/sbt
- https://github.com/sbt/sbt/releases/tag/v1.12.7
