# [M] Outray has a Race Condition in the cli's webapp

## Summary
Severity: Medium
Advisory: GHSA-45hj-9x76-wp9g
CVE: CVE-2026-22819
CWE: CWE-366
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:L/A:H (CVSS_V3)
Published: 2026-01-13
Source: https://github.com/advisories/GHSA-45hj-9x76-wp9g
Type: github-advisory

## Affected
- npm: `outray` — affected >=0 <0.1.5

## Details
### Summary
This vulnerability allows a user i.e a free plan user to get more than the desired subdomains due to lack of db transaction lock mechanisms in `https://github.com/akinloluwami/outray/blob/main/apps/web/src/routes/api/%24orgSlug/subdomains/index.ts`

### Details
- The affected code-:

```ts
//Race condition
        const [subscription] = await db
          .select()
          .from(subscriptions)
          .where(eq(subscriptions.organizationId, organization.id));

        const currentPlan = subscription?.plan || "free";
        const planLimits = getPlanLimits(currentPlan as any);
        const subdomainLimit = planLimits.maxSubdomains;

        const existingSubdomains = await db
          .select()
          .from(subdomains)
          .where(eq(subdomains.organizationId, organization.id));

        if (existingSubdomains.length >= subdomainLimit) {
          return json(
            {
              error: `Subdomain limit reached. The ${currentPlan} plan allows ${subdomainLimit} subdomain${subdomainLimit > 1 ? "s" : ""}.`,
            },
            { status: 403 },
          );
        }

        const existing = await db
          .select()
          .from(subdomains)
          .where(eq(subdomains.subdomain, subdomain))
          .limit(1);

        if (existing.length > 0) {
          return json({ error: "Subdomain already taken" }, { status: 409 });
        }

        const [newSubdomain] = await db
          .insert(subdomains)
          .values({
            id: crypto.randomUUID(),
            subdomain,
            organizationId: organization.id,
            userId: session.user.id,
          })
          .returning();
```

- The first part of the code checks the user plan and determine his/her existing_domains without locking the transaction and allowing it to run.
```ts
const existingSubdomains = await db
          .select()
          .from(subdomains)
          .where(eq(subdomains.organizationId, organization.id));
```

- The other part of the code checks if the desired domain is more than the limit.

```ts
if (existingSubdomains.length >= subdomainLimit) {
          return json(
            {
              error: `Subdomain limit reached. The ${currentPlan} plan allows ${subdomainLimit} subdomain${subdomainLimit > 1 ? "s" : ""}.`,
            },
            { status: 403 },
          );
        }
```

- Finally, it inserts the subdomain also after the whole check without locking transactions.

```ts
const [newSubdomain] = await db
          .insert(subdomains)
          .values({
            id: crypto.randomUUID(),
            subdomain,
            organizationId: organization.id,
            userId: session.user.id,
          })
          .returning();
```
- An attacker can exploit this by making parallel requests to the same endpoint and if the second request reads row `subdomains` before the `INSERT` statement  of request one is made.It allows the attacker to act on a not yet updated row which bypasses the checks and allow the attacker to get more subdomains.For example-:

```
  Parallel request 1                               Parallel  Request  2    
     |                                                                     |
checks for                                                     Checks the not yet updated
available subdomain                                     row and bypasses the logic checks
and determines if it is more than limit
    |                                                                        |
Inserts subdomain and calls it a day           Also inserts the  subdomain
```
-  The attack focuses on exploiting the race window between reading and writing the db rows.

### PoC

- Intercept with Burp proxy,pass to `Repeater` and create multiple requests in a single batch with different subdomain names as seen below. Lastly, send the requests in `parallel`.

<img width="1844" height="855" alt="image" src="https://github.com/user-attachments/assets/f46d5993-31bd-4b96-902a-b2de5b0518bd" />

- Result-:

<img width="1905" height="977" alt="image" src="https://github.com/user-attachments/assets/4c877de2-4b55-46f4-9f1c-78590dfebefc" />


### Impact
The vulnerability provides an infiinite supply of domains to users bypassing the need for subscription

## References
- https://github.com/akinloluwami/outray/security/advisories/GHSA-45hj-9x76-wp9g
- https://github.com/outray-tunnel/outray/security/advisories/GHSA-45hj-9x76-wp9g
- https://nvd.nist.gov/vuln/detail/CVE-2026-22819
- https://github.com/outray-tunnel/outray/commit/08c61495761349e7fd2965229c3faa8d7b1c1581
- https://github.com/outray-tunnel/outray/commit/73e8a09575754fb4c395438680454b2ec064d1d6
- https://github.com/akinloluwami/outray
