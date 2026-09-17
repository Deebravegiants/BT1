# [H] RustFS has SourceIp bypass via spoofed X-Forwarded-For/Real-IP headers

## Summary
Severity: High
Advisory: GHSA-fc6g-2gcp-2qrq
CVE: CVE-2026-21862
CWE: CWE-290
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-02-03
Source: https://github.com/advisories/GHSA-fc6g-2gcp-2qrq
Type: github-advisory

## Affected
- crates.io: `rustfs` — affected >=0 <1.0.0-alpha.78

## Details
### Summary
IP-based access control can be bypassed: get_condition_values trusts client-supplied X-Forwarded-For/X-Real-Ip without verifying a trusted proxy, so any reachable client can spoof aws:SourceIp and satisfy IP-allowlist policies.

### Details

  - Vulnerable code: `rustfs/src/auth.rs:289-304` sets `remote_addr` from `X-Forwarded-For`/`X-Real-Ip`, then inserts `SourceIp` via
    `get_source_ip_raw`, with no trust boundary or proxy validation:
      - `let remote_addr = header.get("x-forwarded-for").and_then(...).or_else(|| header.get("x-real-ip")...).unwrap_or("127.0.0.1");`
      - `args.insert("SourceIp", vec![get_source_ip_raw(header, remote_addr)]);`
  - This value feeds IAM/bucket policy evaluation in `rustfs/src/storage/access.rs` (authorization path), so any request that forges the header can meet `aws:SourceIp` conditions.
  - No authentication is required beyond the request itself; the header is taken at face value even on direct connections.


### PoC

[rustfs-auth-trusted-ip-header-spoofing-poc.tar.gz](https://github.com/user-attachments/files/24038162/rustfs-auth-trusted-ip-header-spoofing-poc.tar.gz)


Steps (already included in `rustfs-auth-trusted-ip-header-spoofing-poc/`):

  1. Start RustFS with two local volumes, e.g.:

```
     mkdir -p /tmp/rustfs-data1 /tmp/rustfs-data2
     RUSTFS_ACCESS_KEY=devadmin RUSTFS_SECRET_KEY=devadmin \
       cargo run --bin rustfs -- --address 0.0.0.0:9000 \
       /tmp/rustfs-data1 /tmp/rustfs-data2
```

  2. From `rustfs-auth-trusted-ip-header-spoofing-poc`/, run:

```
     ENDPOINT=http://127.0.0.1:9000 make run
```

     The script:
      - Creates bucket `rustfs-trusted-ip-poc`.
      - Applies a bucket policy allowing `s3:ListBucket` only from `10.0.0.5/32` (`Principal: {"AWS":["*"]},` Resource array).
      - Sends three unauthenticated `ListBucket` calls:
          - Baseline (no spoof) → HTTP 403.
          - Spoofed `X-Forwarded-For: 10.0.0.5` → HTTP 200 (policy bypass).
          - Spoofed `X-Forwarded-For: 1.2.3.4` → HTTP 403.
      - Responses saved to `poc-baseline.xml`, `poc-spoofed.xml`, `poc-deny.xml`.


### Impact

  - Vulnerability type: Authorization bypass of IP-allowlist (`aws:SourceIp`) via header spoofing.
  - Who is impacted: Any deployment relying on `aws:SourceIp` in IAM/bucket policies for S3 operations. Attackers with network reach to RustFS can forge forwarded-IP headers to gain list/read/write where IP restrictions were meant to block them.

### Credits
Identified by SecMate (https://secmate.dev) automated analysis and validated during manual triage.

## References
- https://github.com/rustfs/rustfs/security/advisories/GHSA-fc6g-2gcp-2qrq
- https://nvd.nist.gov/vuln/detail/CVE-2026-21862
- https://github.com/rustfs/rustfs/commit/b4ba62fa3300b5b258fdc0da141481e3be7ea960
- https://github.com/rustfs/rustfs
