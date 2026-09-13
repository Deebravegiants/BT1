# [M] webfinger.js Blind SSRF Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-8xq3-w9fx-74rv
CVE: CVE-2025-54590
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-07-28
Source: https://github.com/advisories/GHSA-8xq3-w9fx-74rv
Type: github-advisory

## Affected
- npm: `webfinger.js` — affected >=0 <2.8.1

## Details
### Description
The lookup function takes a user address for checking accounts as a feature, however, as per
the ActivityPub spec (https://www.w3.org/TR/activitypub/#security-considerations), on the
security considerations section at B.3, access to Localhost services should be prevented while
running in production. The library does not prevent Localhost access (neither does it prevent
LAN addresses such as 192.168.x.x) , thus is not safe for use in production by ActivityPub
applications. The only check for localhost is done for selecting between HTTP and HTTPS
protocols, and it is done by testing for a host that starts with the string “localhost” and ends with
a port. Anything else (such as “127.0.0.1” or “localhost:1234/abc”) would not be considered
localhost for this test.

In addition, the way that the function determines the host, makes it possible to access any path
in the host, not only “/.well-known/...” paths:

```javascript
if (address.indexOf('://') > -1) {
  // other uri format
  host = address.replace(/ /g,'').split('/')[2];
} else {
  // useraddress
  host = address.replace(/ /g,'').split('@')[1];
}

var uri_index = 0; // track which URIS we've tried already
var protocol = 'https'; // we use https by default

if (self.__isLocalhost(host)) {
  protocol = 'http';
}

function __buildURL() {
  var uri = '';
  if (! address.split('://')[1]) {
  // the URI has not been defined, default to acct
    uri = 'acct:';
  }
  return protocol + '://' + host + '/.well-known/' +URIS[uri_index] + '?resource=' + uri + address;
}
```

If the address is in the format of a user address (user@host.com), the host will be anything
after the first found @ symbol. Since no other test is done, an adversary may pass a specially
crafted address such as user@localhost:7000/admin/restricted_page? and reach pages that
would normally be out of reach. In this example, the code would treat
localhost:7000/admin/restricted_page? as the host, and the created URL would be
https://localhost:7000/admin/restricted_page?/.well-known/webfinger?resource=acct:use
r@localhost:7000/admin/restricted_page?. A server listening on localhost:7000 will then
parse the request as a GET request for the page /admin/restricted_page with the query string
/.well-known/webfinger?resource=acct:user@localhost:7000/admin/restricted_page?.

### PoC and Steps to reproduce
This PoC assumes that there is a server on the machine listening on port 3000, which receives
requests for WebFinger lookups on the address /api/v1/search_user, and then calls the lookup
function in webfinger.js with the user passed as an argument. For the sake of the example we
assume that the server configured webfinger.js with tls_only=false.


1. Activate a local HTTP server listening to port 1234 with a “secret.txt” file:

```
python3 -m http.server 1234
```

2. Run the following command:

```
curl
"http://localhost:3000/api/v1/search_user?search=user@localhost:1234/secret.txt
?"
```

3. View the console of the Python’s HTTP server and see that a request for a
“secret.txt?/.well-known/webfinger?resource=acct:user@localhost:1234/secret.txt
?” file was performed.
This proves that we can redirect the URL to any domain and path we choose, including
localhost and the internal LAN.


### Impact
Due to this issue, any user can cause a server using the library to send GET requests with
controlled host, path and port in an attempt to query services running on the instance’s host or
local network, and attempt to execute a Blind-SSRF gadget in hope of targeting a known
vulnerable local service running on the victim’s machine.


### References
The vulnerability was discovered by Ori Hollander of the JFrog Vulnerability Research team.

## References
- https://github.com/silverbucket/webfinger.js/security/advisories/GHSA-8xq3-w9fx-74rv
- https://nvd.nist.gov/vuln/detail/CVE-2025-54590
- https://github.com/silverbucket/webfinger.js/commit/b5f2f2c957297d25f4d76072963fccaee2e3095a
- https://github.com/silverbucket/webfinger.js
- https://github.com/silverbucket/webfinger.js/releases/tag/v2.8.1
