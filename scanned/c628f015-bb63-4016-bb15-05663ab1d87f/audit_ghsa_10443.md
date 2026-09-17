# [H] Juju has a resource poisoning vulnerability

## Summary
Severity: High
Advisory: GHSA-245v-p8fj-vwm2
CVE: CVE-2025-68153
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-245v-p8fj-vwm2
Type: github-advisory

## Affected
- Go: `github.com/juju/juju` — affected >=0 <0.0.0-20260120044552-26ff93c903d5

## Details
### Summary
Any authenticated user, machine or controller under a Juju controller can modify the resources of an application within the entire controller.

This one is very straightforward to just read in the code:

**Step 1:**
The authorisation mechanism for the resource handler is defined [here](https://github.com/juju/juju/blob/1a8d84ec114c2e4f9921e30081e5a5549f7cbfc4/apiserver/internal/handlers/resources/resources.go#L77). One is only required to have been authed as either a user, machine or controller to pass this check. One requires no permissions on the controller nor does one need any further permissions on the models themselves.

This handler is available under the following path format `/:modeluuid/applications/:application/resources/:resources`. See [here](https://github.com/juju/juju/blob/1a8d84ec114c2e4f9921e30081e5a5549f7cbfc4/apiserver/apiserver.go#L949). The handler defines no authorizer as supported by the handler struct [here](https://github.com/juju/juju/blob/1a8d84ec114c2e4f9921e30081e5a5549f7cbfc4/apiserver/apiserver.go#L696).

One needs to know the following three bits of information to poison the resource cache on the controller:
- model uuid
- application name in the model
- resource name in the model

Given that a lot of deployments use the charm name for applications and the resources for charms are published on charm hub, this is a very low bar to meet, only requiring the model uuid.

**Step 2:**
If one passes the very basic authz check of step 1, one is now allowed free rein for 'PUT' and 'GET' methods to the handler. This security report will only focus on 'PUT' as it is the most interesting. The 'PUT' handler will gladly take whatever is uploaded to it as long as it has the same file extension defined by the resource.

If the resource already exists in the controller's cache, it will be uploaded with whatever is supplied by the upload, see [here](https://github.com/juju/juju/blob/1a8d84ec114c2e4f9921e30081e5a5549f7cbfc4/apiserver/internal/handlers/resources/resources.go#L219) and [here](https://github.com/juju/juju/blob/1a8d84ec114c2e4f9921e30081e5a5549f7cbfc4/domain/resource/service/resource.go#L388).

That is it. One can successfully poison the resource cache for any model in the controller.

### PoC
A proof of concept has not been done for this because it is so obvious from the code read that it is not deemed necessary.

A realistic example of how this can be used: if there is a compromised workload in Juju that has machine credentials, then one can modify the OCI resources for any other model in the controller. For example, if the controller was running a k8s vault, one could change the docker image in use to a trojan horse version that allows obtaining root access to all the vault secrets.

Once this poison has been performed, the attacker can then leverage the vault secrets to go other places.

### Impact
Any charm deployment where a resource could be modified to inject security vulnerabilities into another workload. The most obvious is OCI containers as one gets execution escalation, but if a file resource had security controls in it, this could also be leveraged. For the file case, this would need to be examined on a case-by-case basis.

## References
- https://github.com/juju/juju/security/advisories/GHSA-245v-p8fj-vwm2
- https://nvd.nist.gov/vuln/detail/CVE-2025-68153
- https://github.com/juju/juju/commit/26ff93c903d55b0712c6fb3f6b254710edb971d4
- https://github.com/juju/juju
