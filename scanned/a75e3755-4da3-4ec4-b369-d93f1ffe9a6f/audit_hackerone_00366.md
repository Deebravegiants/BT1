# [C] Unrestricted file upload (RCE)

## Summary
Severity: Critical (CVSS 9.1)
Program: Node.js third-party modules
Weakness: Path Traversal
Reporter: patrickrbc
State: resolved
Disclosed: 2018-06-02T07:20:08.023Z
CVE: CVE-2018-3758
Source: https://hackerone.com/reports/343726

## Details
I would like to report an unrestricted file upload in express-cart.

It allows a user with administrative privileges to upload a file to any path.

# Module

**module name:** express-cart
**version:** 1.1.5
**npm page:** `https://www.npmjs.com/package/express-cart`

## Module Description

expressCart is a fully functional shopping cart built in Node.js (Express, MongoDB) with Stripe, PayPal and Authorize.net payments.

# Vulnerability

## Vulnerability Description

A privileged user can use the upload functionality to gain access to the server.

The application offers the possibility of uploading product images. However, there are many problems with the way it handles these uploads.

Firstly, it uses a path provided by the user. This path is not validated, therefore, it would allow the user to upload the file to any path on the hosting server.

Secondly, it does not restrict the type of the file being uploaded, therefore, it would allow the user to upload a malicious file to gain access to the server.

Finally, it does not restrict the size of the file. This would allow to easily exhaust the host resources and consequently produce a DoS.
  
## Steps To Reproduce:

There are many ways this vulnerability could be exploited. Supposing our goal would be to establish access to the host machine, we could replace the *app.js* file with a malicious JavaScript that would give us a web shell.

Once you have administrator privileges you can use a request similar to:

```
POST /admin/file/upload HTTP/1.1
Host: localhost:1111
Referer: http://localhost:1111/
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/343726_
