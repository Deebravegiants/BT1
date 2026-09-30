# [H] Fedify has an incomplete SSRF mitigation after GHSA-p9cg-vqcc-grcx: validatePublicUrl allows special-use IPv4 ranges

## Summary
Severity: High
Advisory: GHSA-xw9q-2mv6-9fr8
CVE: CVE-2026-50131
CWE: CWE-1286, CWE-1389, CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2026-07-14
Source: https://github.com/advisories/GHSA-xw9q-2mv6-9fr8
Type: github-advisory

## Affected
- npm: `@fedify/fedify` — affected >=0.11.2 <1.9.12
- npm: `@fedify/fedify` — affected >=1.10.0 <1.10.11
- npm: `@fedify/fedify` — affected >=2.0.0 <2.0.19
- npm: `@fedify/fedify` — affected >=2.1.0 <2.1.15
- npm: `@fedify/fedify` — affected >=2.2.0 <2.2.4
- npm: `@fedify/vocab-runtime` — affected >=0 <2.0.19
- npm: `@fedify/vocab-runtime` — affected >=2.1.0 <2.1.15
- npm: `@fedify/vocab-runtime` — affected >=2.2.0 <2.2.4

## Details
### Summary

Fedify previously addressed SSRF/internal network access in GHSA-p9cg-vqcc-grcx by adding public URL validation before runtime document and media fetching. However, the current IPv4 validation logic appears incomplete.

The `validatePublicUrl()` protection relies on `isValidPublicIPv4Address()` to reject non-public IPv4 destinations. The function blocks common private and local ranges such as `10.0.0.0/8`, `127.0.0.0/8`, `169.254.0.0/16`, `172.16.0.0/12`, and `192.168.0.0/16`, but it still treats several special-use, reserved, multicast, benchmarking, and carrier-grade NAT IPv4 ranges as valid public destinations.

Because this validation is used as an SSRF defense before outbound fetches, this appears to be an incomplete mitigation or bypass class for the previous SSRF issue.

I tested this against the current repository code at unreleased version 2.3.0. I used `>=0.11.2, <=2.2.3` as the suspected affected range because 0.11.2 is listed as a patched version for GHSA-p9cg-vqcc-grcx, and this report concerns the post-fix validation logic. Maintainers may adjust the exact affected range.

### Why this is not a duplicate of GHSA-p9cg-vqcc-grcx

GHSA-p9cg-vqcc-grcx covered the original behavior where Fedify fetched ActivityPub object, activity, document, and media URLs without first ensuring that the resolved destination was public.

This report is about the post-fix validation logic. The current mitigation now performs public URL/IP validation, but the IPv4 classification is incomplete and still treats several special-use ranges as public. Therefore, this is a potential incomplete fix/bypass of the previous SSRF mitigation rather than a re-report of the original issue.

The affected behavior appears to exist in the patched/current code path, not only in versions listed as vulnerable in the original advisory.

### Affected Code

Affected file:

`packages/vocab-runtime/src/url.ts`

Current IPv4 validation logic:

```ts
export function isValidPublicIPv4Address(address: string): boolean {
  const parts = address.split(".");
  const first = parseInt(parts[0]);
  if (first === 0 || first === 10 || first === 127) return false;
  const second = parseInt(parts[1]);
  if (first === 169 && second === 254) return false;
  if (first === 172 && second >= 16 && second <= 31) return false;
  if (first === 192 && second === 168) return false;
  return true;
}
```

The important point is that the bypass exists in the mitigation logic itself: the function responsible for deciding whether a destination is public returns true for address ranges that are not globally routable public internet destinations.

### Proof of Concept

I reproduced the IPv4 validation behavior using the same logic:

```ts
function isValidPublicIPv4Address(address) {
  const parts = address.split(".");
  const first = parseInt(parts[0], 10);
  if (first === 0 || first === 10 || first === 127) return false;

  const second = parseInt(parts[1], 10);
  if (first === 169 && second === 254) return false;
  if (first === 172 && second >= 16 && second <= 31) return false;
  if (first === 192 && second === 168) return false;

  return true;
}

const tests = [
  "8.8.8.8",
  "127.0.0.1",
  "10.0.0.1",
  "192.168.1.1",
  "169.254.169.254",
  "100.64.0.1",
  "198.18.0.1",
  "224.0.0.1",
  "240.0.0.1",
  "192.0.0.1",
  "192.0.2.1",
  "198.51.100.1",
  "203.0.113.1"
];

for (const ip of tests) {
  console.log(ip + " => " + isValidPublicIPv4Address(ip));
}
```

Observed output:

```
8.8.8.8 => true
127.0.0.1 => false
10.0.0.1 => false
192.168.1.1 => false
169.254.169.254 => false
100.64.0.1 => true
198.18.0.1 => true
224.0.0.1 => true
240.0.0.1 => true
192.0.0.1 => true
192.0.2.1 => true
198.51.100.1 => true
203.0.113.1 => true
```

The validator correctly blocks some common private and local ranges, but incorrectly allows multiple special-use ranges.

### Examples of incorrectly allowed ranges

Important examples include:

```
100.64.0.0/10 Carrier-grade NAT
198.18.0.0/15 Benchmarking / internal testing networks
224.0.0.0/4 Multicast
240.0.0.0/4 Reserved
192.0.0.0/24 IETF protocol assignments
```

Additional correctness examples:

```
192.0.2.0/24 Documentation range
198.51.100.0/24 Documentation range
203.0.113.0/24 Documentation range
```

## Security Impact

Any Fedify feature that accepts or processes remote ActivityPub object, activity, document, or media URLs and relies on validatePublicUrl() as an SSRF protection boundary may incorrectly allow outbound requests to special-use IPv4 destinations that should not be treated as public internet resources.

This may allow an attacker-controlled ActivityPub object or media URL to cause a Fedify server to initiate requests to non-public or special-use network ranges, depending on the deployment environment and network routing.

This is best understood as an incomplete fix/bypass class for the previous SSRF/internal-network-access advisory GHSA-p9cg-vqcc-grcx.

## Suggested Fix

Avoid using a small manual denylist for public IP validation. Instead, validate that the resolved address is globally routable/public.

At minimum, IPv4 validation should reject all relevant special-use ranges, including:

```
0.0.0.0/8
10.0.0.0/8
100.64.0.0/10
127.0.0.0/8
169.254.0.0/16
172.16.0.0/12
192.0.0.0/24
192.0.2.0/24
192.168.0.0/16
198.18.0.0/15
198.51.100.0/24
203.0.113.0/24
224.0.0.0/4
240.0.0.0/4
```

A safer long-term fix would be to use a maintained IP address classification library that explicitly supports security-sensitive public/global IP validation.

Patch Idea

```ts
export function isValidPublicIPv4Address(address: string): boolean {
  const parts = address.split(".").map((part) => parseInt(part, 10));

  if (
    parts.length !== 4 ||
    parts.some((part) => Number.isNaN(part) || part < 0 || part > 255)
  ) {
    return false;
  }

  const [a, b] = parts;

  if (a === 0) return false;
  if (a === 10) return false;
  if (a === 100 && b >= 64 && b <= 127) return false;
  if (a === 127) return false;
  if (a === 169 && b === 254) return false;
  if (a === 172 && b >= 16 && b <= 31) return false;
  if (a === 192 && b === 0) return false;
  if (a === 192 && b === 168) return false;
  if (a === 198 && (b === 18 || b === 19)) return false;
  if (a === 198 && b === 51) return false;
  if (a === 203 && b === 0) return false;
  if (a >= 224) return false;

  return true;
}
```


## Advisory Classification Note

I understand this may be classified either as a new advisory or as an update/incomplete fix for GHSA-p9cg-vqcc-grcx. Since the issue appears to affect the validation logic added after the original SSRF fix, and because the affected code is part of the current security boundary for outbound URL fetching, I wanted to report it privately for maintainer review.

## Disclosure Note

This report does not attempt to access any real internal network service. The proof focuses on the validation decision itself: multiple non-public or special-use IPv4 ranges are accepted as public by the current SSRF protection logic.



## Researcher

Reported by Chaitanya Garware.

## References
- https://github.com/fedify-dev/fedify/security/advisories/GHSA-xw9q-2mv6-9fr8
- https://nvd.nist.gov/vuln/detail/CVE-2026-50131
- https://github.com/fedify-dev/fedify
