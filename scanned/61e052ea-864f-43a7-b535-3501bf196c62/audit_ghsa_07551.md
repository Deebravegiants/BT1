# [H] Compressing Vulnerable to Arbitrary File Write via Symlink Extraction

## Summary
Severity: High
Advisory: GHSA-cc8f-xg8v-72m3
CVE: CVE-2026-24884
CWE: CWE-59
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-03
Source: https://github.com/advisories/GHSA-cc8f-xg8v-72m3
Type: github-advisory

## Affected
- npm: `compressing` — affected >=2.0.0 <2.0.1
- npm: `compressing` — affected >=0 <1.10.4

## Details
# Arbitrary File Write via Symlink Extraction in `github.com/node-modules/compressing`

## Brief Introduction

The `compressing` npm package extracts TAR archives while restoring symbolic links without validating their targets. 
By embedding symlinks that resolve outside the intended extraction directory, an attacker can cause subsequent file entries to be written to arbitrary locations on the host file system.

Depending on the extractor’s handling of existing files, this behavior may allow overwriting sensitive files or creating new files in security-critical locations.

## Affected Component and Versions

- **Component**: `github.com/node-modules/compressing`
- **Affected Versions**: `<= 1.10.3 || =2.0.0` 

## Vulnerability Details

### Root Cause

`compressing.tar.uncompress` sanitizes the destination paths of archive entries, but it does **not** restrict or validate the targets of symlinks contained in TAR archives. During extraction, the library creates those symlinks inside the output directory. Later entries that resolve through the symlink are written to the symlink target rather than the intended extraction root, enabling an arbitrary file write.

### Impact

An attacker who can supply a crafted TAR archive can:

- Cause files to be written outside the intended extraction directory (arbitrary file write via symlink traversal).

- Write files to attacker-controlled paths on the host file system once symbolic links are followed during extraction.

- In environments where extraction is performed with elevated privileges or targets executable paths, this may lead to code execution, privilege escalation, data corruption, or denial of service.

## Reproduction

### Environment

- **OS**: Ubuntu 24.04
- **Node.js**: v24.12.0
- **compressing**: 2.0.0

### Construct PoC Archive

The following pseudo-code demonstrates the attack logic:

```python
base_dir = "archive/"
with tarfile.open("./poc_arbitrary_write.tar", mode="w") as tar:
    add_regular_file(tar, base_dir + "baseFile.txt", "base content\n")
    add_symlink(tar, base_dir + "myTmp", "/tmp")
    add_regular_file(tar, base_dir + "myTmp/poc.txt", "Arbitrary File Write\n")
```

### Extract the Archive

```javascript
const compressing = require('compressing');

function untar(archiveName, destPath) {
  return compressing.tar.uncompress(archiveName, destPath);
}


async function main() {
  const archivePath = process.argv[2];
  const destPath = "./output";

  if (archivePath && archivePath.endsWith(".tar")) {
    await untar(archivePath, destPath);
  }
}

main();
```

### Attack Results

<img width="547" height="161" alt="image" src="https://github.com/user-attachments/assets/5ea12efd-0d3f-4f8a-8414-b3a5c72e153e" />


After extraction, the output directory contains a symlink pointing to `/tmp`. The file `poc.txt` is then written through the symlink to `/tmp/poc.txt`, demonstrating an arbitrary file write outside the extraction directory.

## Summary

`compressing` restores symlinks from TAR archives without validating their targets. By combining a malicious symlink with a subsequent file entry, an attacker can redirect extracted files to arbitrary locations on the host.

## References
- https://github.com/node-modules/compressing/security/advisories/GHSA-cc8f-xg8v-72m3
- https://nvd.nist.gov/vuln/detail/CVE-2026-24884
- https://github.com/node-modules/compressing/commit/8d16c196c7f1888fc1af957d9ff36117247cea6c
- https://github.com/node-modules/compressing/commit/ce1c0131c401c071c77d5a1425bf8c88cfc16361
- https://github.com/node-modules/compressing
