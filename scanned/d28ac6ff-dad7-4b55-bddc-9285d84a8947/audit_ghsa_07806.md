# [C] Keylime Missing Authentication for Critical Function and Improper Authentication

## Summary
Severity: Critical
Advisory: GHSA-4jqp-9qjv-57m2
CVE: CVE-2026-1709
CWE: CWE-295, CWE-306
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:H (CVSS_V3)
Published: 2026-02-06
Source: https://github.com/advisories/GHSA-4jqp-9qjv-57m2
Type: github-advisory

## Affected
- PyPI: `keylime` — affected >=7.12.0 <7.12.2
- PyPI: `keylime` — affected >=7.13.0 <7.13.1

## Details
### Impact

The Keylime registrar does not enforce mutual TLS (mTLS) client certificate authentication since version 7.12.0. The registrar's TLS context is configured with `ssl.CERT_OPTIONAL` instead of `ssl.CERT_REQUIRED`, allowing any client to connect to protected API endpoints without presenting a valid client certificate.

**Who is impacted:**
  - All Keylime deployments running versions 7.12.0 through 7.13.0
  - Environments where the registrar HTTPS port (default 8891) is network-accessible to untrusted clients

**What an attacker can do:**
  - **List all registered agents** (`GET /v2/agents/`) - enumerate the entire agent inventory
  - **Retrieve agent details** (`GET /v2/agents/{uuid}`) - obtain public TPM keys, certificates, and network locations (IP/port) of any agent
  - **Delete any agent** (`DELETE /v2/agents/{uuid}`) - remove agents from the registry, disrupting attestation services

Note: The exposed TPM data (EK, AK, certificates) consists of public keys and certificates. Private keys remain protected within TPM hardware. The HMAC secret used for challenge-response validation is stored in the database but is not exposed via the API.

**Affected versions:** >= 7.12.0, <= 7.13.0

**Fixed versions:** 7.12.2, >= 7.13.1

### Patches

A patch for the affected released versions is available. It removes the line that override the configuration of `ssl.verify_mode`, leaving the `CERT_REQUIRED` value set by `web_util.init_mtls()`:

```diff
diff --git a/keylime/web/base/server.py b/keylime/web/base/server.py
index 1d9a9c2..859b23a 100644
--- a/keylime/web/base/server.py
+++ b/keylime/web/base/server.py
@@ -2,7 +2,6 @@ import asyncio
 import multiprocessing
 from abc import ABC, abstractmethod
 from functools import wraps
-from ssl import CERT_OPTIONAL
 from typing import TYPE_CHECKING, Any, Callable, Optional

 import tornado
@@ -252,7 +251,6 @@ class Server(ABC):
         self._https_port = config.getint(component, "tls_port", fallback=0)
         self._max_upload_size = config.getint(component, "max_upload_size", fallback=104857600)
         self._ssl_ctx = web_util.init_mtls(component)
-        self._ssl_ctx.verify_mode = CERT_OPTIONAL

     def _get(self, pattern: str, controller: type["Controller"], action: str, allow_insecure: bool = False) -> None:
         """Creates a new route to handle incoming GET requests issued for paths which match the given
```

Users should upgrade to the patched version once it is released.

### Workarounds

If upgrading is not immediately possible, apply one of the following mitigations:

#### 1. Network isolation (Recommended)

Restrict access to the registrar HTTPS port (default 8891) using firewall rules
to allow only trusted hosts (verifier, tenant):

##### Example using iptables
```
iptables -A INPUT -p tcp --dport 8891 -s <verifier_ip> -j ACCEPT
iptables -A INPUT -p tcp --dport 8891 -s <tenant_ip> -j ACCEPT
iptables -A INPUT -p tcp --dport 8891 -j DROP
```

#### 2. Reverse proxy with mTLS enforcement

Deploy a reverse proxy (nginx, HAProxy) in front of the registrar that enforces client certificate authentication:

##### Example nginx configuration
```
server {
    listen 8891 ssl;
    ssl_certificate /path/to/server.crt;
    ssl_certificate_key /path/to/server.key;
    ssl_client_certificate /path/to/ca.crt;
    ssl_verify_client on;  # Enforce client certificates

    location / {
        proxy_pass https://localhost:8892;  # Internal registrar port
    }
}
```

## References
- https://github.com/keylime/keylime/security/advisories/GHSA-4jqp-9qjv-57m2
- https://nvd.nist.gov/vuln/detail/CVE-2026-1709
- https://access.redhat.com/errata/RHSA-2026:2224
- https://access.redhat.com/errata/RHSA-2026:2225
- https://access.redhat.com/errata/RHSA-2026:2298
- https://access.redhat.com/security/cve/CVE-2026-1709
- https://bugzilla.redhat.com/show_bug.cgi?id=2435514
- https://github.com/keylime/keylime
- https://github.com/pypa/advisory-database/tree/main/vulns/keylime/PYSEC-2026-74.yaml
