# [C] NextAuth.js before 4.10.3 and 3.29.10 sending verification requests (magic link) to unwanted emails

## Summary
Severity: Critical
Advisory: GHSA-xv97-c62v-4587
CVE: CVE-2022-35924
CWE: CWE-20, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-08-02
Source: https://github.com/advisories/GHSA-xv97-c62v-4587
Type: github-advisory

## Affected
- npm: `next-auth` — affected >=4.0.0 <4.10.3
- npm: `next-auth` — affected >=0 <3.29.10

## Details
### Impact
`next-auth` users who are using the `EmailProvider` either in versions before `4.10.3` or `3.29.10` are affected.

If an attacker could forge a request that sent a comma-separated list of emails (eg.: `attacker@attacker.com,victim@victim.com`) to the sign-in endpoint, NextAuth.js would send emails to both the attacker and the victim's e-mail addresses. The attacker could then login as a newly created user with the email being `attacker@attacker.com,victim@victim.com`. This means that basic authorization like `email.endsWith("@victim.com")` in the `signIn` callback would fail to communicate a threat to the developer and would let the attacker bypass authorization, even with an `@attacker.com` address.

### Patches
We patched this vulnerability in `v4.10.3` and `v3.29.10` by normalizing the email value that is sent to the sign-in endpoint before accessing it anywhere else. We also added a `normalizeIdentifier` callback on the `EmailProvider` configuration, where you can further tweak your requirements for what your system considers a valid e-mail address. (E.g.: strict RFC2821 compliance)

To upgrade, run one of the following:
```sh
npm i next-auth@latest
```
```sh
yarn add next-auth@latest
```
```sh
pnpm add next-auth@latest
```

(This will update to the latest v4 version, but you can change `latest` to `3` if you want to stay on v3. This is not recommended. v3 is unmaintained.)

### Workarounds
If for some reason you cannot upgrade, you can normalize the incoming request like the following, using Advanced Initialization:
```ts
// pages/api/auth/[...nextauth].ts

function normalize(identifier) {
  // Get the first two elements only,
  // separated by `@` from user input.
  let [local, domain] = identifier.toLowerCase().trim().split("@")
  // The part before "@" can contain a ","
  // but we remove it on the domain part
  domain = domain.split(",")[0]
  return `${local}@${domain}`
}

export default async function handler(req, res) {
  if (req.body.email) req.body.email = normalize(req.body.email)
  return await NextAuth(req, res, {/* your options */ })
}
```

### References
- EmailProvider: https://next-auth.js.org/providers/email
- Normalize the email address: https://next-auth.js.org/providers/email#normalizing-the-email-address
- Email syntax: https://en.wikipedia.org/wiki/Email_address#Local-part
- `signIn` callback: https://next-auth.js.org/configuration/callbacks#sign-in-callback
- Advanced Initialization: https://next-auth.js.org/configuration/initialization#advanced-initialization
- `nodemailer` address: https://nodemailer.com/message/addresses

### For more information

If you have any concerns, we request responsible disclosure, outlined here: https://next-auth.js.org/security#reporting-a-vulnerability

### Timeline

The issue was reported 26th of July, a response was sent out in less than 1 hour and after identifying the issue a patch was published within 5 working days.

### Acknowledgments

We would like to thank [Socket](https://socket.dev) for disclosing this vulnerability in a responsible manner and following up until it got published.

## References
- https://github.com/nextauthjs/next-auth/security/advisories/GHSA-xv97-c62v-4587
- https://nvd.nist.gov/vuln/detail/CVE-2022-35924
- https://github.com/nextauthjs/next-auth/commit/afb1fcdae3cc30445038ef588e491d139b916003
- https://en.wikipedia.org/wiki/Email_address#Local-part
- https://github.com/nextauthjs/next-auth
- https://next-auth.js.org/configuration/callbacks#sign-in-callback
- https://next-auth.js.org/configuration/initialization#advanced-initialization
- https://next-auth.js.org/providers/email
- https://next-auth.js.org/providers/email#normalizing-the-e-mail-address
- https://next-auth.js.org/providers/email#normalizing-the-email-address
- https://nodemailer.com/message/addresses
