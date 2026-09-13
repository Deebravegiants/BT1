# [M] Juju affected by Confused Deputy IDOR attack via Predictable user specified ID in Juju Secrets

## Summary
Severity: Medium
Advisory: GHSA-5cj2-rqqf-hx9p
CVE: CVE-2026-32694
CWE: CWE-343
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-19
Source: https://github.com/advisories/GHSA-5cj2-rqqf-hx9p
Type: github-advisory

## Affected
- Go: `github.com/juju/juju` — affected >=0.0.0-20221021155847-35c560704ee2 <0.0.0-20260319091847-d06919eb03ec

## Details
### Summary

Predictable secret ID and lack of secret origin API enable confused deputy attacks on Juju workloads.

### Details

A Juju application can create a secret and grant it to another integrated application (grantee).

When they do so, the secret owner has to communicate the secret id to the grantee.

The grantee, having received the secret id can load the secret content and perform operations on behalf of the secret owner.

However, today the grantee has no way to determine which granted secret belongs to which owner.

Instead the grantee relies on:
- being able to read the secret by id (secret was in fact granted, by some entity)
- secret id was received over a relation (the remote end of the relation is presumed to be secret owner)

Additionally, secret IDs are XID, which are predictable, here two secrets created by two distinct apps in the same K8s model close in time:
```
d34vsl7mp25c76301hs0
time (UTC): 2025-09-17 00:18:28 (Unix 1758068308)
machine: f6c88a
pid: 50072
counter: 6294648

d34vslfmp25c76301hsg
time (UTC): 2025-09-17 00:18:29 (Unix 1758068309)
machine: f6c88a
pid: 50072
counter: 6294649
```

### PoC

This allows for an IDOR attack where:
- actors:
  - a **Good** application (the owner of the _Victim_),
  - an **Evil** application, and
  - a **Provider** application (the _Confused Deputy_)
- relations: **Good** --- **Provider**, **Evil** --- **Provider**
- secrets: **Good** and **Evil** create _Secrets_, granting them to the **Provider** and communicate _Secret IDs_ with the **Provider**.
- semantics: the **Provider** performs some operation on behalf of the **Good**/**Evil** using the _Secret_.
- weakness 1: **Evil** can guess the _Secret ID_ that **Good** granted and communicated to **Provider**.
- weakness 2: _Juju_ doesn't provide the **Provider** application the facility to verify the provenance of the _Secret IDs_.
- exploit: **Evil** passes **Good**'s secret id to **Provider**.
- bypass: **Provider** performs _evil_ operation with **Good**'s _Secret ID_ on behalf of **Evil**.

**Evil** could benefit by:
- exfiltrating **Good**'s _Secret_ via reflection.
- reading or mutating **Good**'s resources accessible via **Good*'s _Secret_.

### Impact

This requires a complex setup.

Not all shared secrets are used like above, so an actual exploit requires a very specific relation interface, specific semantics of the data in the databag, and an administrator having a reasonable need to deploy two apps (one evil, one good) related to the same (third) provider app.

If exploited, it can be very hard to determine what went wrong after the fact.

### Suggested remediation

#### 1. Longer, random secret IDs

For example, if the secret id was extended with a 128-bit nonce, guessing a sibling secret ID would be infeasible, and an attack of this style would require another weakness (e.g. secret IDs exposed in logs)

#### 2. Grantee secret API

Today, an app is not allowed to call `secret-info-get` on the granted secret.
Additionally, granted secrets are not included in the `secret-ids` output.

Suppose that the Provider could run these hook tools:
```command
(provider/0)> secret-ids
my-own-secret-123

(provider/0)> secret-ids --grants
good-secret-id-42
evil-secret-id-43

(provider/0)> secret-info-get good-secret-id-42
good-secret-id-42:
  revision: 1
  label: ""
  owner: good
  grant-relation-id: 12
  rotation: never
```

The Provider would then able to validate the secret ID it's about to use against:
- the relation in which the secret ID has been passed (good relation 12 or evil relation 14)
- the application or unit name of the secret owner (good or evil)

## References
- https://github.com/juju/juju/security/advisories/GHSA-5cj2-rqqf-hx9p
- https://nvd.nist.gov/vuln/detail/CVE-2026-32694
- https://github.com/juju/juju/commit/d06919eb03ec68156818bcc304b5fe1c39a8f9e9
- https://github.com/juju/juju
