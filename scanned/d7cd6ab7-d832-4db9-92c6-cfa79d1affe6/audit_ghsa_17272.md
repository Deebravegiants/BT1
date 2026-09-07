# [M] Open Redirect Vulnerability in Taguette

## Summary
Severity: Medium
Advisory: GHSA-5923-r76v-mprm
CVE: CVE-2025-67502
CWE: CWE-601
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-12-09
Source: https://github.com/advisories/GHSA-5923-r76v-mprm
Type: github-advisory

## Affected
- PyPI: `taguette` — affected >=0 <1.5.2

## Details
## Summary

An Open Redirect vulnerability exists in Taguette that allows attackers to craft malicious URLs that redirect users to arbitrary external websites after authentication. This can be exploited for phishing attacks where victims believe they are interacting with a trusted Taguette instance but are redirected to a malicious site designed to steal credentials or deliver malware.

**Severity:** Medium to High  

---

## Details

The application accepts a user-controlled `next` parameter and uses it directly in HTTP redirects without any validation. The vulnerable code is located in two places:

### Location 1: Login Handler (`taguette/web/views.py`, lines 140-144)

```python
def _go_to_next(self):
    next_ = self.get_argument('next', '')
    if not next_:
        next_ = self.reverse_url('index')
    return self.redirect(next_)  # ← No validation of next_ parameter
```

This method is called after successful login (line 132) and when an already-logged-in user visits the login page (line 109).

### Location 2: Cookies Prompt Handler (`taguette/web/views.py`, lines 79-85)

```python
def post(self):
    self.set_cookie('cookies_accepted', 'yes', dont_check=True)
    next_ = self.get_argument('next', '')
    if not next_:
        next_ = self.reverse_url('index')
    return self.redirect(next_)  # ← No validation of next_ parameter
```

In both cases, if `next_` is provided by the user, it is passed directly to `self.redirect()` without checking whether it points to the same host or is a relative URL.

---

[![pic](https://github.com/user-attachments/assets/ac0afe1f-a8ac-4ac0-88f5-1c2cd092ca46)](url)


## PoC

Simply replace `[your-taguette-instance]` with your Taguette server domain and test these URLs in your browser:

### Test 1: Cookies Prompt Redirect

```
https://[your-taguette-instance]/cookies?next=https://google.com
```

1. Open the URL above in your browser
2. Click "Accept cookies" button
3. **Result:** You are redirected to `https://google.com` (external site)

### Test 2: Login Redirect

```
https://[your-taguette-instance]/login?next=https://google.com
```

1. Open the URL above in your browser
2. Log in with valid credentials
3. **Result:** You are redirected to `https://google.com` (external site)

### Test 3: Already Logged In Redirect

```
https://[your-taguette-instance]/login?next=https://google.com
```

1. First, log in to Taguette normally
2. Then open the URL above
3. **Result:** You are immediately redirected to `https://google.com`

> **Note:** We use `google.com` as a safe external site for testing. In a real attack, this would be a phishing site.

---

## Impact

- **Who is affected:** All users of any Taguette instance running in multi-user mode
- **Attack vector:** Social engineering / phishing via crafted URLs
- **Exploitability:** Trivial - requires only crafting a URL with a malicious `next` parameter
- **Consequences:**
  - Credential theft through phishing
  - Malware distribution
  - Session hijacking
  - Reputation damage to organizations running Taguette instances

The vulnerability is particularly dangerous because:
1. The login page displayed is completely legitimate, building victim trust
2. Users have just entered their credentials, making them more likely to enter them again on a fake "session expired" page
3. The trusted domain in the URL makes the attack more convincing

---

## Recommended Fix

Validate that the `next` parameter is either a relative URL or points to the same host before redirecting.

### Example Fix

Add a validation function:

```python
from urllib.parse import urlparse

def is_safe_url(url, host):
    """Check if URL is safe for redirect (relative or same host)."""
    if not url:
        return False
    parsed = urlparse(url)
    # Reject protocol-relative URLs (//evil.com)
    if url.startswith('//'):
        return False
    # Allow relative URLs (no scheme and no netloc)
    if not parsed.scheme and not parsed.netloc:
        return True
    # Allow same-host URLs
    return parsed.netloc == host
```

Then update the vulnerable methods:

```python
def _go_to_next(self):
    next_ = self.get_argument('next', '')
    if not next_ or not is_safe_url(next_, self.request.host):
        next_ = self.reverse_url('index')
    return self.redirect(next_)
```

Apply the same fix to the `CookiesPrompt.post()` method.

---

## References
- https://github.com/remram44/taguette/security/advisories/GHSA-5923-r76v-mprm
- https://nvd.nist.gov/vuln/detail/CVE-2025-67502
- https://github.com/remram44/taguette/commit/67de2d2612e7e2572c61cd9627f89c2bfd0f2a36
- https://github.com/remram44/taguette
