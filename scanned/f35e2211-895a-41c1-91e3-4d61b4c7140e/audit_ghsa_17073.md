# [C] Budibase affected by VM2 Constructor Escape Vulnerability

## Summary
Severity: Critical
Advisory: GHSA-4g2x-vq5p-5vj6
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-03-01
Source: https://github.com/advisories/GHSA-4g2x-vq5p-5vj6
Type: github-advisory

## Affected
- npm: `@budibase/server` — affected >=0 <2.20.0

## Details
### Impact
Previously, budibase used a library called `vm2` for code execution inside the Budibase builder and apps, such as the UI below for configuring bindings in the design section.

![Screenshot 2024-03-01 at 13 50 16](https://github.com/Budibase/budibase/assets/11256663/5f049b64-cd99-48fd-a184-644cd312c82e)

Due to a [vulnerability in vm2](https://github.com/advisories/GHSA-cchq-frgv-rjh5), any environment that executed the code server side (automations and column formulas) was susceptible to this vulnerability, allowing users to escape the sandbox provided by `vm2`, and to expose server side variables such as `process.env`. It's recommended by the authors of `vm2` themselves that you should move to another solution for remote JS execution due to this vulnerability.

### Patches
We moved our entire JS sandbox infrastructure over to `isolated-vm`, a much more secure and recommended library for remote code execution in 2.20.0. This also comes with a performance benefit in the way we cache and execute your JS server side. The budibase cloud platform has been patched already and is not running `vm2`, but self host users will need to manage the updates by themselves.

If you are a self hosted user, you can take the following steps to reproduce the exploit and to verify if your installation is currently affected.

Create a new formula column on one of your tables in the data section with the following configuration.
![Screenshot 2024-03-01 at 14 04 28](https://github.com/Budibase/budibase/assets/11256663/0f8bc19b-9e44-4e95-ab4e-6ef6278eea34)

Add the following JS function to the formula and save.
![Screenshot 2024-03-01 at 14 05 19](https://github.com/Budibase/budibase/assets/11256663/1d0c9705-1a88-49b0-93e0-f385a04b5c25)

If your installation is vulnerable, when the formula evaluates you will be able to see the printed `process.env` in your new formula field. If not, your installation is not affected.

### Workarounds
There is no workaround at this time for any budibase app that uses JS. You must fully migrate post version 2.20.0 to patch the vulnerability.

### References
- https://github.com/advisories/GHSA-cchq-frgv-rjh5

## References
- https://github.com/Budibase/budibase/security/advisories/GHSA-4g2x-vq5p-5vj6
- https://github.com/patriksimek/vm2/security/advisories/GHSA-cchq-frgv-rjh5
- https://github.com/Budibase/budibase/commit/601c02a4acc695b1cc602bf611f0ae66d6e5868f
- https://github.com/Budibase/budibase
