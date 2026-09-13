# [M] mcp-memory-service Vulnerable to System Information Disclosure via Health Endpoint

## Summary
Severity: Medium
Advisory: GHSA-73hc-m4hx-79pj
CVE: CVE-2026-29787
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-03-05
Source: https://github.com/advisories/GHSA-73hc-m4hx-79pj
Type: github-advisory

## Affected
- PyPI: `mcp-memory-service` — affected >=0 <10.21.0

## Details
### Summary
The `/api/health/detailed` endpoint returns detailed system information including OS version, Python version, CPU count, memory totals, disk usage, and the full database filesystem path. When `MCP_ALLOW_ANONYMOUS_ACCESS=true` is set (required for the HTTP server to function without OAuth/API key), this endpoint is accessible without authentication. Combined with the default `0.0.0.0` binding, this exposes sensitive reconnaissance data to the entire network.

### Details
### Vulnerable Code

**`health.py:90-101` - System information collection**

```python
system_info = {
    "platform": platform.system(),              # e.g., "Linux", "Darwin"
    "platform_version": platform.version(),     # Full OS kernel version string
    "python_version": platform.python_version(),# e.g., "3.12.1"
    "cpu_count": psutil.cpu_count(),            # CPU core count
    "memory_total_gb": round(memory_info.total / (1024**3), 2),
    "memory_available_gb": round(memory_info.available / (1024**3), 2),
    "memory_percent": memory_info.percent,
    "disk_total_gb": round(disk_info.total / (1024**3), 2),
    "disk_free_gb": round(disk_info.free / (1024**3), 2),
    "disk_percent": round((disk_info.used / disk_info.total) * 100, 2)
}
```

**`health.py:131-132` - Database path disclosure**

```python
if hasattr(storage, 'db_path'):
    storage_info["database_path"] = storage.db_path  # Full filesystem path
```

### Authentication Bypass Path

The `/api/health/detailed` endpoint uses `require_read_access` which calls `get_current_user`. When `MCP_ALLOW_ANONYMOUS_ACCESS=true`, the auth middleware grants access:

```python
# middleware.py:372-379
if ALLOW_ANONYMOUS_ACCESS:
    logger.debug("Anonymous access explicitly enabled, granting read-only access")
    return AuthenticationResult(
        authenticated=True,
        client_id="anonymous",
        scope="read",
        auth_method="none"
    )
```

**Note**: The basic `/health` endpoint (line 68) has **no auth dependency at all** and returns version and uptime information unconditionally.

### Information Exposed

| Field | Example Value | Reconnaissance Value |
|-------|--------------|---------------------|
| `platform` | `"Linux"` | OS fingerprinting |
| `platform_version` | `"#1 SMP PREEMPT_DYNAMIC..."` | Kernel version → CVE targeting |
| `python_version` | `"3.12.1"` | Python CVE targeting |
| `cpu_count` | `8` | Resource enumeration |
| `memory_total_gb` | `32.0` | Infrastructure profiling |
| `database_path` | `"/home/user/.mcp-memory/memories.db"` | Username + file path disclosure |
| `database_size_mb` | `45.2` | Data volume estimation |

### Attack Scenario

1. Attacker scans the local network for services on port 8000
2. Finds mcp-memory-service with HTTP enabled and anonymous access
3. Calls `GET /api/health/detailed`  (no credentials needed)
4. Receives OS version, Python version, full database path (revealing username), system resources
5. Uses this information to:
   - Target known CVEs for the specific OS/Python version
   - Identify the database file location for potential direct access
   - Profile the system for further attacks
 
### PoC

```python
# Show the system info that would be exposed
import platform, psutil

system_info = {
    "platform": platform.system(),
    "platform_version": platform.version(),
    "python_version": platform.python_version(),
    "cpu_count": psutil.cpu_count(),
    "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
}
print(system_info)  # All of this is returned to unauthenticated users
```

### Impact
- **OS fingerprinting**: Exact OS and kernel version enables targeted exploit selection
- **Path disclosure**: Database path reveals username, home directory structure, and file locations
- **Resource enumeration**: CPU, memory, and disk info reveal infrastructure scale
- **Reconnaissance enablement**: Combined information significantly reduces attacker effort for follow-up attacks

## Remediation

1. **Remove system details from default health endpoint** - return only `status`, `version`, `uptime`:

```python
@router.get("/health/detailed")
async def detailed_health_check(
    storage: MemoryStorage = Depends(get_storage),
    user: AuthenticationResult = Depends(require_write_access)  # Require admin/write access
):
    # Only return storage stats, not system info
    ...
```

2. **Do not expose `database_path`** - this leaks the filesystem structure:

```python
# Remove or redact
# storage_info["database_path"] = storage.db_path  # REMOVE THIS
```

3. **Add auth to basic `/health`** or limit it to status-only (no version):

```python
@router.get("/health")
async def health_check():
    return {"status": "healthy"}  # No version, no uptime
```
Alternatively, **Bind to `127.0.0.1` by default** instead of `0.0.0.0`, preventing network-based reconnaissance entirely:

```python
# In config.py — change default from '0.0.0.0' to '127.0.0.1'
HTTP_HOST = os.getenv('MCP_HTTP_HOST', '127.0.0.1')
```

Users who need network access can explicitly set `MCP_HTTP_HOST=0.0.0.0`, making the exposure a conscious opt-in rather than a default.

## References
- https://github.com/doobidoo/mcp-memory-service/security/advisories/GHSA-73hc-m4hx-79pj
- https://nvd.nist.gov/vuln/detail/CVE-2026-29787
- https://github.com/doobidoo/mcp-memory-service/commit/18f4323ca92763196aa2922f691dfbeb6bd84e48
- https://github.com/doobidoo/mcp-memory-service
