# [H] Deno's AES GCM authentication tags are not verified

## Summary
Severity: High
Advisory: GHSA-2x3r-hwv5-p32x
CVE: CVE-2025-24015
CWE: CWE-347
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-06-04
Source: https://github.com/advisories/GHSA-2x3r-hwv5-p32x
Type: github-advisory

## Affected
- crates.io: `deno` — affected >=1.46.0 <2.1.7
- crates.io: `deno_node` — affected >=0.102.0 <0.125.0

## Details
### Summary

This affects AES-256-GCM and AES-128-GCM in Deno, introduced by commit [0d1beed](https://github.com/denoland/deno/commit/0d1beed). Specifically, the authentication tag is not being validated. This means tampered ciphertexts or incorrect keys might not be detected, which breaks the guarantees expected from AES-GCM. Older versions of Deno correctly threw errors in such cases, as does Node.js.

Without authentication tag verification, AES-GCM degrades to essentially CTR mode, removing integrity protection. Authenticated data set with set_aad is also affected, as it is incorporated into the GCM hash (ghash) but this too is not validated, rendering AAD checks ineffective.

### PoC

```ts
import { Buffer } from "node:buffer";
import {
  createCipheriv,
  createDecipheriv,
  randomBytes,
  scrypt,
} from "node:crypto";

type Encrypted = {
  salt: string;
  iv: string;
  enc: string;
  authTag: string;
};

const deriveKey = (key: string, salt: Buffer) =>
  new Promise<Buffer>((res, rej) =>
    scrypt(key, salt, 32, (err, k) => {
      if (err) rej(err);
      else res(k);
    })
  );

async function encrypt(text: string, key: string): Promise<Encrypted> {
  const salt = randomBytes(32);
  const k = await deriveKey(key, salt);

  const iv = randomBytes(16);
  const enc = createCipheriv("aes-256-gcm", k, iv);
  const ciphertext = enc.update(text, "binary", "binary") + enc.final("binary");

  return {
    salt: salt.toString("binary"),
    iv: iv.toString("binary"),
    enc: ciphertext,
    authTag: enc.getAuthTag().toString("binary"),
  };
}

async function decrypt(enc: Encrypted, key: string) {
  const k = await deriveKey(key, Buffer.from(enc.salt, "binary"));
  const dec = createDecipheriv("aes-256-gcm", k, Buffer.from(enc.iv, "binary"));

  const out = dec.update(enc.enc, "binary", "binary");
  dec.setAuthTag(Buffer.from(enc.authTag, "binary"));
  return out + dec.final("binary");
}

const test = await encrypt("abcdefghi", "key");
test.enc = "";
console.log(await decrypt(test, "")); // no error
```

### Impact

While discovered through experimentation, authentication failures that should raise errors may be silently ignored.

## References
- https://github.com/denoland/deno/security/advisories/GHSA-2x3r-hwv5-p32x
- https://nvd.nist.gov/vuln/detail/CVE-2025-24015
- https://github.com/denoland/deno/commit/0d1beed
- https://github.com/denoland/deno/commit/0d1beed2e3633d71d5e288e0382b85be361ec13d
- https://github.com/denoland/deno/commit/4f27d7cdc02e3edfb9d36275341fb8185d6e99ed
- https://github.com/denoland/deno/commit/a4003a5292bd0affefad3ecb24a8732886900f67
- https://github.com/denoland/deno
