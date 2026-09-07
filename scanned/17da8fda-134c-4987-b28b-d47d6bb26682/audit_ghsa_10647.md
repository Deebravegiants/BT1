# [M] RustFS has an authorization bypass in multipart UploadPartCopy enables cross-bucket object exfiltration

## Summary
Severity: Medium
Advisory: GHSA-mx42-j6wv-px98
CVE: CVE-2026-39360
CWE: CWE-862
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-mx42-j6wv-px98
Type: github-advisory

## Affected
- crates.io: `rustfs` — affected >=0

## Details
RustFS contains a missing authorization check in the multipart copy path (`UploadPartCopy`). A low-privileged user who cannot read objects from a victim bucket can still exfiltrate victim objects by copying them into an attacker-controlled multipart upload and completing the upload.

This breaks tenant isolation in multi-user / multi-tenant deployments.

## Impact
**Unauthorized cross-bucket / cross-tenant data exfiltration (Confidentiality: High).**

An attacker with only minimal permissions on their own bucket (multipart upload + Put/Get on destination objects) can copy and retrieve objects from a victim bucket **without** having `s3:GetObject` (or equivalent) permission on the source.

In the attached PoC, the attacker successfully exfiltrates a 5MB private object and proves integrity via matching SHA256 and size.

## Threat Model (Realistic)
- **Victim tenant/user** owns a bucket (e.g., `victim-bucket-*`) and stores private objects (e.g., `private/finance_dump.bin`).
- **Attacker tenant/user** has **no permissions** on the victim bucket:
  - cannot `ListObjects`, `HeadObject`, `GetObject`, or `CopyObject` from the victim bucket.
- Attacker has **minimal permissions only on attacker bucket**:
  - `CreateMultipartUpload`, `UploadPart`, `UploadPartCopy`, `CompleteMultipartUpload`, `AbortMultipartUpload`,
  - and `PutObject`/`GetObject` for objects in attacker bucket.
- Despite this, attacker can exfiltrate victim objects via multipart copy.

## Root Cause Analysis
The access control layer fails open for multipart copy-related operations:

File: `rustfs/src/storage/access.rs`
- `abort_multipart_upload()` returns `Ok(())` without authorization (L435–437)
- `complete_multipart_upload()` returns `Ok(())` without authorization (L442–444)
- `upload_part_copy()` returns `Ok(())` without authorization (L1446–1448)

In contrast, `copy_object()` correctly enforces authorization:
- source `GetObject` authorization (L469)
- destination `PutObject` authorization (L478)

The multipart copy implementation reads the source object directly:

File: `rustfs/src/app/multipart_usecase.rs`
- `store.get_object_reader(&src_bucket, &src_key, ...)` (L959–962)

Because `upload_part_copy()` does not enforce source `GetObject` authorization, the server reads and copies victim data even when the requester lacks permission.

## Affected Versions
- **Tested vulnerable on:** `main` @ `c1d5106acc3480c275a52344df84633bb6dcd8f0`
- **Git describe:** `1.0.0-alpha.86-3-gc1d5106a`

The fail-open authorization behavior for `UploadPartCopy` was introduced in:
- **Commit:** `09ea11c13` (per `git blame` on `rustfs/src/storage/access.rs:1443-1448`)

**Affected range (recommended wording):**
- All versions **from** commit `09ea11c13` **through** `c1d5106acc3480c275a52344df84633bb6dcd8f0` (and likely any releases containing those commits) until a fix is applied.

### Package version (Cargo metadata)
- `rustfs` crate version in this tree: **0.0.5** (`cargo metadata`)

## Proof of Concept (PoC) – Real Commands + Verified Results

### Files
Place the PoC script at the repository root:

- **PoC script:** [`poc_uploadpartcopy_exfil_v3.sh`](https://github.com/user-attachments/files/26006935/poc_uploadpartcopy_exfil_v3.sh)
- **Captured output:** [`poc_v3_output.txt`](https://github.com/user-attachments/files/26006938/poc_v3_output.txt)
- *(Optional)* **Redacted debug log:** `upload_part_copy_debug_redacted.log` (Authorization/signature redacted)

### Environment 
RustFS running locally (Docker is simplest), listening on:

- `http://127.0.0.1:9000`

Tools:
- `awscli`, `jq`, `awscurl`

### Steps to Reproduce
1) Start RustFS (example):

```bash
docker compose -f docker-compose-simple.yml up -d
````

2. Run the PoC and save output:

```bash
chmod +x poc_uploadpartcopy_exfil_v3.sh
./poc_uploadpartcopy_exfil_v3.sh | tee poc_v3_output.txt
```

### Attachments

* [`poc_uploadpartcopy_exfil_v3.sh`](https://github.com/user-attachments/files/26006950/poc_uploadpartcopy_exfil_v3.sh)
* [`poc_v3_output.txt`](https://github.com/user-attachments/files/26006953/poc_v3_output.txt)


### Expected Behavior

* Attacker operations against victim bucket should be denied:

  * `ListObjects` -> AccessDenied
  * `HeadObject` -> AccessDenied
  * `GetObject` -> AccessDenied
  * `CopyObject` -> AccessDenied
* `UploadPartCopy` from victim -> attacker multipart should also be denied.

### Actual Behavior

* All direct operations against victim are denied (as expected),
* but **`UploadPartCopy` succeeds**, and attacker retrieves the copied object from attacker bucket.

### Observed PoC Output 

Victim uploads a private object:

* size: `5,242,880` bytes
* sha256: `fda018db1da9d8f4c1b287c75943384a3b4ede391ec156039b6d94e17d6ad68f`

Attacker exfiltrates it via multipart copy:

* stolen size: `5,242,880` bytes
* stolen sha256: `fda018db1da9d8f4c1b287c75943384a3b4ede391ec156039b6d94e17d6ad68f`

Proof:

* hashes and sizes match (victim == stolen) -> unauthorized cross-bucket read confirmed.

## Network Evidence (Redacted)

The debug log shows a successful request with:

* HTTP method: `PUT`
* destination: `/<attacker-bucket>/<dst-key>?partNumber=1&uploadId=...`
* header: `x-amz-copy-source: <victim-bucket>/private/finance_dump.bin`
* response: `HTTP/1.1 200` with `<CopyPartResult><ETag>...</ETag>...</CopyPartResult>`


## Fix

Implement authorization checks equivalent to `copy_object()` for multipart copy paths:

* `upload_part_copy`:

  * enforce **source** `GetObject` authorization on `x-amz-copy-source`
  * enforce **destination** `PutObject` authorization on the target object
  * (recommended) apply the same tag-condition enforcement used by `copy_object()` on the source.

* `complete_multipart_upload`:

  * enforce destination `PutObject` authorization

* `abort_multipart_upload`:

  * enforce appropriate multipart permission (or destination `PutObject` as a safe boundary)

## References
- https://github.com/rustfs/rustfs/security/advisories/GHSA-mx42-j6wv-px98
- https://nvd.nist.gov/vuln/detail/CVE-2026-39360
- https://github.com/rustfs/rustfs
