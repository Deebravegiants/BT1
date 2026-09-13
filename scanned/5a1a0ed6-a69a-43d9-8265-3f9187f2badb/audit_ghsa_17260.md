# [M] Authentication Bypass via Default JWT Secret in NocoBase docker-compose Deployments

## Summary
Severity: Medium
Advisory: GHSA-mv7p-34fv-4874
CVE: CVE-2025-13877
CWE: CWE-1320, CWE-321
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:L/VI:L/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-12-09
Source: https://github.com/advisories/GHSA-mv7p-34fv-4874
Type: github-advisory

## Affected
- npm: `@nocobase/auth` — affected >=1.9.0 <1.9.23
- npm: `@nocobase/auth` — affected >=0 <1.9.0-beta.18
- npm: `@nocobase/auth` — affected >=2.0.0-alpha.1 <2.0.0-alpha.52

## Details
### Impact

CVE-2025-13877 is an **authentication bypass vulnerability caused by insecure default JWT key usage** in NocoBase Docker deployments.

Because the official one-click Docker deployment configuration historically provided a **public default JWT key**, attackers can **forge valid JWT tokens without possessing any legitimate credentials**. By constructing a token with a known `userId` (commonly the administrator account), an attacker can directly bypass authentication and authorization checks.

Successful exploitation allows an attacker to:

- Bypass authentication entirely
- Impersonate arbitrary users
- Gain full administrator privileges
- Access sensitive business data
- Create, modify, or delete users
- Access cloud storage credentials and other protected secrets

The vulnerability is **remotely exploitable**, requires **no authentication**, and **public proof-of-concept exploits are available**.  
This issue is functionally equivalent in impact to other JWT secret exposure vulnerabilities such as **CVE-2024-43441** and **CVE-2025-30206**.

Deployments that used the default Docker configuration without explicitly overriding the JWT secret are affected.

---

### Patches

✅ The vulnerability has been **fully patched** through a secure JWT key management redesign.

The remediation enforces the following security guarantees:

- JWT secrets are no longer allowed to fall back to public default values.
- Secrets must either:
  - Be explicitly provided by the user, or
  - Be securely generated using cryptographically strong randomness at first startup.
- Generated secrets are persisted securely with restricted filesystem permissions.
- Invalid or weak secret values immediately trigger a startup failure.

✅ Fixed Versions:
- **NocoBase ≥ 1.9.23**
- **NocoBase ≥ 1.9.0-beta.18**
- **NocoBase ≥ 2.0.0-alpha.52**

---

### Workarounds

If upgrading is not immediately possible, the following temporary mitigations **must** be performed to reduce risk:

1. Explicitly set a **strong, randomly generated JWT secret** via environment variables `APP_KEY`.
2. **Restart all running NocoBase instances** so the new secret takes effect.
3. **Invalidate all existing JWT sessions**, forcing complete user re-authentication.
4. Verify that **no default secret values** are present in:
   - `docker-compose.yml`
   - `.env` files
   - Kubernetes Secrets

---

### References

- **CVE Record:** CVE-2025-13877  
- **VulDB Entry:** https://vuldb.com/?id.334033  
- **Public Exploit Proof:**  
  https://gist.github.com/H2u8s/f3ede60d7ecfe598ae452aa5a8fbb90d  

- **Affected Default Docker Configurations:**  
  - https://github.com/nocobase/nocobase/blob/main/docker/app-mysql/docker-compose.yml#L13  
  - https://github.com/nocobase/nocobase/blob/main/docker/app-mariadb/docker-compose.yml#L13  
  - https://github.com/nocobase/nocobase/blob/main/docker/app-postgres/docker-compose.yml#L11  
  - https://github.com/nocobase/nocobase/blob/main/docker/app-sqlite/docker-compose.yml#L11  

- **Official Deployment Documentation:**  
  - https://docs.nocobase.com/welcome/getting-started/installation/docker-compose  
  - https://v2.docs.nocobase.com/get-started/installation/docker

## References
- https://github.com/nocobase/nocobase/security/advisories/GHSA-mv7p-34fv-4874
- https://nvd.nist.gov/vuln/detail/CVE-2025-13877
- https://github.com/nocobase/nocobase/commit/de4292ea7847dd26c6306445091769f8b9ee96d5
- https://docs.nocobase.com/welcome/getting-started/installation/docker-compose
- https://gist.github.com/H2u8s/f3ede60d7ecfe598ae452aa5a8fbb90d
- https://github.com/nocobase/nocobase
- https://github.com/nocobase/nocobase/blob/main/docker/app-mariadb/docker-compose.yml#L13
- https://github.com/nocobase/nocobase/blob/main/docker/app-mysql/docker-compose.yml#L13
- https://github.com/nocobase/nocobase/blob/main/docker/app-postgres/docker-compose.yml#L11
- https://github.com/nocobase/nocobase/blob/main/docker/app-sqlite/docker-compose.yml#L11
- https://v2.docs.nocobase.com/get-started/installation/docker
- https://vuldb.com/?ctiid.334033
- https://vuldb.com/?id.334033
- https://vuldb.com/?submit.692205
