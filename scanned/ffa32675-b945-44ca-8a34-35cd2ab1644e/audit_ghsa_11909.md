# [H] nginx-UI has Unencrypted Storage of DNS API Tokens and ACME Private Keys

## Summary
Severity: High
Advisory: GHSA-5hf2-vhj6-gj9m
CVE: CVE-2026-33030
CWE: CWE-639, CWE-78
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-30
Source: https://github.com/advisories/GHSA-5hf2-vhj6-gj9m
Type: github-advisory

## Affected
- Go: `github.com/0xJacky/nginx-ui` — affected >=0

## Details
## Summary

Nginx-UI contains an Insecure Direct Object Reference (IDOR) vulnerability that allows any authenticated user to access, modify, and delete resources belonging to other users. The application's base `Model` struct lacks a `user_id` field, and all resource endpoints perform queries by ID without verifying user ownership, enabling complete authorization bypass in multi-user environments.

## Severity

**High** - CVSS 3.1 Score: **8.8 (High)**

Vector String: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H`

**Note**: Original score was 7.5. The score was updated to 8.8 after discovering that sensitive data (DNS API tokens, ACME private keys) is stored in plaintext, which when combined with IDOR allows immediate credential theft without decryption.

## Product

nginx-ui

## Affected Versions

All versions up to and including v2.3.3

## CWE

CWE-639: Authorization Bypass Through User-Controlled Key

## Description

### Exposed DNS Provider Credentials

The `dns.Config` structure (`internal/cert/dns/config_env.go`) contains API credentials:

```go
type Configuration struct {
    Credentials map[string]string `json:"credentials"`  // API tokens here
    Additional  map[string]string `json:"additional"`
}
```

| Provider | Credential Fields | Impact if Leaked |
|----------|------------------|------------------|
| Cloudflare | `CF_API_TOKEN` | Full DNS zone control |
| Alibaba Cloud DNS | `ALICLOUD_ACCESS_KEY`, `ALICLOUD_SECRET_KEY` | Full DNS control + potential IAM access |
| Tencent Cloud DNS | `TENCENTCLOUD_SECRET_ID`, `TENCENTCLOUD_SECRET_KEY` | Full DNS control |
| AWS Route53 | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` | Route53 + potential AWS access |
| GoDaddy | `GODADDY_API_KEY`, `GODADDY_API_SECRET` | DNS record modification |

### Combined Attack: IDOR + Plaintext Storage

When the IDOR vulnerability is combined with plaintext storage, attackers can directly extract API tokens from other users' resources:

```
Attack Chain:
┌─────────────────────────────────────────────────────────────────┐
│ 1. Attacker authenticates with low-privilege account            │
│ 2. Uses IDOR to enumerate: /api/dns_credentials/1,2,3...      │
│ 3. Reads plaintext API tokens directly from HTTP response       │
│ 4. No decryption needed - tokens stored in cleartext            │
│ 5. Uses stolen tokens to:                                       │
│    - Modify DNS records (domain hijacking)                      │
│    - Issue fraudulent SSL certificates                          │
│    - Pivot to cloud infrastructure                              │
└─────────────────────────────────────────────────────────────────┘
```

### PoC: Extracting Plaintext Credentials via IDOR

```bash
# Attacker with low-privilege token accessing admin's DNS credential
curl -H "Authorization: $ATTACKER_TOKEN" \
     https://nginx-ui.example.com/api/dns_credentials/1

# Response contains PLAINTEXT API token (no decryption required):
{
    "id": 1,
    "name": "Production Cloudflare",
    "provider": "cloudflare",
    "config": {
        "credentials": {
            "CF_API_TOKEN": "yhyQ7xR...plaintext_token_visible..."
        }
    }
}
```

### Updated CVSS Score with Plaintext Storage

The plaintext storage increases the confidentiality impact:

**CVSS 3.1 Score: 8.8 (High)**

Vector: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H`

- **Scope Changed (S:C)**: Impact extends to external services (DNS providers, cloud platforms)
- **High Confidentiality (C:H)**: Plaintext API tokens immediately usable
- **High Integrity (I:H)**: DNS records, certificates can be modified
- **High Availability (A:H)**: Services can be disrupted via DNS/certificate manipulation

---

### Attack Scenario: Certificate Hijacking

```
1. Attacker creates low-privilege account on nginx-ui
2. Uses IDOR to enumerate all DNS credentials: /api/dns_credentials/1,2,3...
3. Steals Cloudflare API token from admin's credential
4. Uses token to:
   - Modify DNS records
   - Issue fraudulent Let's Encrypt certificates
   - Intercept traffic to victim domains
```

## Credit

Discovered by security researcher during authorized security audit.

## Recommendation

### Immediate Mitigation

1. **Add User Ownership to Models**

```go
// model/model.go
type Model struct {
    ID        uint64          `gorm:"primary_key" json:"id"`
    UserID    uint64          `gorm:"index" json:"user_id"`  // Add this field
    CreatedAt time.Time       `json:"created_at"`
    UpdatedAt time.Time       `json:"updated_at"`
    DeletedAt *gorm.DeletedAt `gorm:"index" json:"deleted_at,omitempty"`
}
```

2. **Filter Queries by Current User**

```go
// api/certificate/dns_credential.go
func GetDnsCredential(c *gin.Context) {
    id := cast.ToUint64(c.Param("id"))
    currentUser := c.MustGet("user").(*model.User)

    d := query.DnsCredential
    dnsCredential, err := d.Where(
        d.ID.Eq(id),
        d.UserID.Eq(currentUser.ID),  // Add user filter
    ).First()

    if err != nil {
        cosy.ErrHandler(c, err)
        return
    }
    // ...
}
```

3. **Add Authorization Middleware**

```go
// middleware/authorization.go
func RequireOwnership(resourceType string) gin.HandlerFunc {
    return func(c *gin.Context) {
        currentUser := c.MustGet("user").(*model.User)
        resourceID := cast.ToUint64(c.Param("id"))

        // Check if resource belongs to current user
        ownerID, err := getResourceOwner(resourceType, resourceID)
        if err != nil || ownerID != currentUser.ID {
            c.AbortWithStatusJSON(http.StatusForbidden, gin.H{
                "message": "Access denied",
            })
            return
        }
        c.Next()
    }
}
```

### Database Migration

```sql
-- Add user_id column to all resource tables
ALTER TABLE dns_credentials ADD COLUMN user_id BIGINT;
ALTER TABLE certs ADD COLUMN user_id BIGINT;
ALTER TABLE acme_users ADD COLUMN user_id BIGINT;
ALTER TABLE sites ADD COLUMN user_id BIGINT;
ALTER TABLE streams ADD COLUMN user_id BIGINT;
ALTER TABLE configs ADD COLUMN user_id BIGINT;

-- Set default owner for existing resources
UPDATE dns_credentials SET user_id = 1 WHERE user_id IS NULL;
UPDATE certs SET user_id = 1 WHERE user_id IS NULL;

-- Add foreign key constraint
ALTER TABLE dns_credentials ADD CONSTRAINT fk_dns_credentials_user
    FOREIGN KEY (user_id) REFERENCES users(id);
```

### Long-term Improvements

1. Implement role-based access control (RBAC)
2. Add audit logging for resource access
3. Implement resource sharing functionality with explicit permissions
4. Add integration tests for authorization checks

---

## Remediation for Plaintext Storage

### Immediate Fix: Encrypt Sensitive Fields

Apply the same `serializer:json[aes]` pattern used for S3 credentials to DNS and ACME data:

**model/dns_credential.go:**
```go
type DnsCredential struct {
    Model
    Name         string      `json:"name"`
    Config       *dns.Config `json:"config,omitempty" gorm:"serializer:json[aes]"` // Add AES encryption
    Provider     string      `json:"provider"`
    ProviderCode string      `json:"provider_code" gorm:"index"`
}
```

**model/acme_user.go:**
```go
type AcmeUser struct {
    Model
    // ...
    Key PrivateKey `json:"-" gorm:"serializer:json[aes]"` // Add AES encryption
    // ...
}
```

### Data Migration

Existing plaintext data must be re-saved to trigger encryption:

```go
func MigrateSensitiveData() error {
    // Migrate DNS credentials
    var dnsCreds []model.DnsCredential
    query.DnsCredential.Find(&dnsCreds)
    for _, cred := range dnsCreds {
        query.DnsCredential.Save(&cred) // Re-save triggers AES encryption
    }

    // Migrate ACME users
    var acmeUsers []model.AcmeUser
    query.AcmeUser.Find(&acmeUsers)
    for _, user := range acmeUsers {
        query.AcmeUser.Save(&user)
    }

    return nil
}
```

### Summary of Required Changes

| File | Line | Current | Fix |
|------|------|---------|-----|
| `model/dns_credential.go` | 7 | `serializer:json` | `serializer:json[aes]` |
| `model/acme_user.go` | Key field | `serializer:json` | `serializer:json[aes]` |

## References

- [CWE-639: Authorization Bypass Through User-Controlled Key](https://cwe.mitre.org/data/definitions/639.html)
- [OWASP IDOR Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Insecure_Direct_Object_Reference_Prevention_Cheat_Sheet.html)
- [PortSwigger: IDOR Vulnerabilities](https://portswigger.net/web-security/access-control/idor)

## Disclosure Timeline

- **2026-03-13**: Vulnerability discovered through source code audit
- **2026-03-13**: Vulnerability successfully reproduced in local Docker environment
- **2026-03-13**: All IDOR operations verified: READ, MODIFY, DELETE
- **2026-03-13**: Security advisory prepared
- **[Pending]**: Report submitted to nginx-ui maintainers
- **[Pending]**: CVE ID requested
- **[Pending]**: Patch developed and tested
- **[Pending]**: Public disclosure (21-90 days after vendor notification)

## References
- https://github.com/0xJacky/nginx-ui/security/advisories/GHSA-5hf2-vhj6-gj9m
- https://nvd.nist.gov/vuln/detail/CVE-2026-33030
- https://github.com/0xJacky/nginx-ui
- https://github.com/0xJacky/nginx-ui/releases/tag/v2.3.4
