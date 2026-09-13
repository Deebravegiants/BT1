# [H] @budibase/backend-core has potential SSRF DNS rebinding bypass in outbound fetch validation

## Summary
Severity: High
Advisory: GHSA-gfq7-5x4g-3xhf
CVE: CVE-2026-54353
CWE: CWE-367, CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-06-22
Source: https://github.com/advisories/GHSA-gfq7-5x4g-3xhf
Type: github-advisory

## Affected
- npm: `@budibase/backend-core` — affected >=0 <3.39.9

## Details
Summary

Authenticated users with automation permissions can bypass Budibase's SSRF blacklist through DNS rebinding.

The outbound fetch flow validates a hostname against the blacklist before the request is sent, but the actual socket connection later performs a separate DNS lookup through node-fetch. Since the validated IPs are never pinned to the connection, an attacker-controlled hostname can return a public IP during validation and a private/internal IP during the real connection.

This results in a non-blind SSRF primitive against internal services reachable from the Budibase host, including loopback, RFC1918 ranges, and cloud metadata endpoints.

Details

The issue comes from the outbound fetch validation flow resolving DNS twice:

During blacklist validation
Again during the real socket connection

The first lookup result is discarded after validation, so the second lookup is free to resolve to a different IP.

This creates a classic TOCTOU DNS rebinding issue.

Affected flow in:

packages/backend-core/src/utils/outboundFetch.ts
```
async function throwIfUnsafe(url: string): Promise<void> {
  const parsed = parseUrl(url)

  if (await isBlacklisted(parsed.hostname)) {
    throw new Error("URL is blocked or could not be resolved safely.")
  }
}

for (let redirects = 0; redirects <= MAX_REDIRECTS; redirects++) {
  await throwIfUnsafe(nextUrl)

  const response = await fetchFn(nextUrl, nextRequest)

  // ...
}
```
fetchFn uses plain node-fetch with no custom http.Agent / https.Agent, so the underlying socket performs its own independent dns.lookup after validation completes.

The same pattern also exists in:

packages/server/src/automations/steps/utils.ts
```
await throwIfBlacklisted(nextUrl)

const response = await fetch(nextUrl, nextRequest)
```
The blacklist implementation resolves hostnames but only returns a boolean:

packages/backend-core/src/blacklist/blacklist.ts
```
async function lookup(address: string): Promise<string[]> {
  address = parseAddress(address)

  const addresses = await performLookup(address, { all: true })

  return addresses.map(addr => addr.address)
}

export async function isBlacklisted(address: string): Promise<boolean> {
  // ...

  if (!net.isIP(address)) {
    try {
      ips = await lookup(address)
    } catch (e) {
      /* ... */
    }
  } else {
    ips = [address]
  }

  return ips.some(ip => blackList!.check(ip, getIpVersion(ip)))
}
```
The resolved IPs are discarded, so callers cannot pin the later socket connection to the validated addresses.

An attacker controlling authoritative DNS for a hostname can therefore return:

a public IP during validation
a private/internal IP during the actual connection

Anything routing through these helpers inherits the issue, including:

outgoing webhook
Slack
Discord
Make
Zapier
n8n
AI extract
object-store fetches

Several of these steps return upstream response content directly into automation output, which makes the SSRF non-blind.

PoC

Tested locally against a self-hosted build from master.
No Budibase-operated infrastructure was touched.

Run Budibase locally.

Start a harmless local HTTP listener:

python3 -m http.server 8080 --bind 127.0.0.1

Use a rebinding hostname such as:

7f000001.cb007264.rbndr.us

which rotates between:

127.0.0.1
203.0.113.100

Steps to reproduce:

Log into Budibase with automation permissions.
Create an automation using the Outgoing Webhook step.
Set the URL to:
http://<rebinding-host>:8080/
Trigger the automation.

Observed result:

The blacklist validation resolves the hostname to the public IP and allows the request.
node-fetch performs a second DNS lookup during socket creation.
The second lookup resolves to 127.0.0.1.
The TCP connection lands on the local service.
The local server response body appears directly in the automation output.
Impact

This produces a non-blind read-SSRF primitive against anything reachable from the Budibase host process, including:

loopback services (127.0.0.1)
RFC1918 ranges
internal Kubernetes/VPC services
cloud metadata endpoints (169.254.169.254)

On cloud deployments without IMDSv2 enforcement, this may expose temporary IAM credentials via:

/latest/meta-data/iam/security-credentials/<role>

On multi-tenant hosted deployments, this may also create potential cross-tenant access paths through shared internal infrastructure.

## References
- https://github.com/Budibase/budibase/security/advisories/GHSA-gfq7-5x4g-3xhf
- https://nvd.nist.gov/vuln/detail/CVE-2026-54353
- https://github.com/Budibase/budibase
