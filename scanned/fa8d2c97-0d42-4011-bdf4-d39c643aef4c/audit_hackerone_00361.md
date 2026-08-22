# [C] Privilege escalation allows any user to add an administrator

## Summary
Severity: Critical (CVSS 9.9)
Program: Node.js third-party modules
Weakness: Privilege Escalation
Reporter: patrickrbc
State: resolved
Disclosed: 2018-07-12T07:57:47.724Z
CVE: CVE-2018-16483
Source: https://hackerone.com/reports/343626

## Details
I would like to report privilege escalation in the npm module express-cart.

It allows a normal user to add another user with administrator privileges.

# Module

**module name:** express-cart
**version:** 1.1.5
**npm page:** `https://www.npmjs.com/package/express-cart`

## Module Description

expressCart is a fully functional shopping cart built in Node.js (Express, MongoDB) with Stripe, PayPal and Authorize.net payments.

## Module Stats

[10] weekly downloads

# Vulnerability

## Vulnerability Description

A deficiency in the access control allows normal users from expressCart to add new users to the application. This behavior by itself might be considered a privilege escalation. However, it was also possible to add the user as administrator.

## Steps To Reproduce:

Firstly, I noticed that all the endpoints located in the *user.js* file are not being restricted by the *common.restrict* middleware, as the other admin routes do.  Also, the endpoint */admin/user/insert* does not check if the user is admin before adding a new user, which I guess it would be a unlikely behavior.

The following code is used to check if it is the first time creating a user:

```
// set the account to admin if using the setup form. Eg: First user account
let urlParts = url.parse(req.header('Referer'));

let isAdmin = false;
if(urlParts.path === '/admin/setup'){
  isAdmin = true;
}
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/343626_
