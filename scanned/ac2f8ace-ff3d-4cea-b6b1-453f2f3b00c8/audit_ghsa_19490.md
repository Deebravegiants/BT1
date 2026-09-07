# [H] Kyverno vulnerable to bypass of policy rules that use namespace selectors in match statements

## Summary
Severity: High
Advisory: GHSA-jrr2-x33p-6hvc
CVE: CVE-2025-46342
CWE: CWE-1287
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-04-29
Source: https://github.com/advisories/GHSA-jrr2-x33p-6hvc
Type: github-advisory

## Affected
- Go: `github.com/kyverno/kyverno` — affected >=0 <1.13.5
- Go: `github.com/kyverno/kyverno` — affected >=1.14.0-alpha.1 <1.14.0

## Details
### Summary

Due to a missing error propagation in function `GetNamespaceSelectorsFromNamespaceLister` in `pkg/utils/engine/labels.go` it may happen that policy rules using namespace selector(s) in their `match` statements are mistakenly not applied during admission review request processing. As a consequence, security-critical mutations and validations are bypassed, potentially allowing attackers with K8s API access to perform malicious operations.

### Details

As a policy engine Kyverno is a critical component ensuring the security of Kubernetes clusters by apply security-relevant policy rules in the Kubernetes admission control process.

We encountered a case where Kyverno did not apply policy rules which should have been applied.  This happened in both the mutation and the validation phase of admission control.  Effectively Kyverno handled the admission review requests as
if those policy rules did not exist.  Consequently, the Kube API request was accepted without applying security-relevant patches and validations.

As the root cause we identified a missing error propagation in function `GetNamespaceSelectorsFromNamespaceLister` in `pkg/utils/engine/labels.go` ([src][1]).

All affected policy rules use a namespace selector in their match resource filters like this:

```yaml
match:
  all:
  - resources:
      namespaceSelector:
        matchExpressions:
        - key: label1
          operator: Exists
```

Such specification intents to apply rules only to resource objects which reside in a namespace whose labels match the given label expressions.

When Kyverno handles an admission webhook, function `GetNamespaceSelectorsFromNamespaceLister` in package
`github.com/kyverno/kyverno/pkg/utils/engine` ([src][1]) is called to retrieve the labels of the request object's namespace.  This function gets the namespace object from a `"k8s.io/client-go/listers/core/v1".NamespaceLister`.  In case the
namespace lister returns an error, `GetNamespaceSelectorsFromNamespaceLister` does NOT propagate this error to its caller, but returns an empty label map, which is equivalent to a namespace without any labels.

The returned label map is later used to select matching policy rules.  If a rule has a resource filter with namespace selector, it will be mistakenly excluded or included.

The namespace lister fails to return the namespace object if the underlying `SharedIndexInformer` has not (yet) updated its cache.  Those updates happen based on watch events from the Kube API Server, which does not guarantee any maximum delivery time.  If the Kube API Server handling the watch is under high load or otherwise impaired (e.g. requests to etcd take longer due to pending leader election in HA setup) then informer cache updates can be delayed significantly.  However, we did not find a way to reliably reproduce such condition.

To bypass Kyverno policies, an attacker may try to exploit the described misbehavior by:

- putting the Kube API Server under load before sending requests that Kyverno policies should be bypassed for.

- sending many request with a high rate to Kube API Server.

We did not try any of such attack vectors and therefore cannot prove their effectiveness.

In our scenario the Kyverno policies apply to pods in "sandbox" namespaces identified as such by certain labels.  Those single-use namespaces and the pods therein are frequently created (and removed) by other controllers.  Therefore, Kyverno often receives admission webhooks for objects whose namespace has been created shortly before.

#### Correction Proposal

Function `GetNamespaceSelectorsFromNamespaceLister` in package `github.com/kyverno/kyverno/pkg/utils/engine` ([src][1]) should return an error instead of an empty label map in case it could not get the namespace object from the namespace lister.  This error will then cause admission webhook processing to fail, which lets Kubernetes fail the Kube API request if the policy's failure policy is `Fail` (a must for security-relevant policies).

In addition, function `GetNamespaceSelectorsFromNamespaceLister` could retry (with deadline) to get the namespace object from the namespace lister in case of a NotFound error.  But as admission webhook processing time should be kept as short as possible, this might not be a good idea.

Another option would be to perform a GET request for the namespace as a fallback in case the namespace lister returns a NotFound error.

### PoC

We did not find a way to reliably reproduce such case.

### Impact

Administrators attempting to enforce cluster security through Kyverno policies, but that allow less privileged users or service accounts to create/update/delete resources.


[1]: https://github.com/kyverno/kyverno/blob/a96b1a4794b4d25cb0c6d72c05fc6355e95cf65c/pkg/utils/engine/labels.go#L10

## References
- https://github.com/kyverno/kyverno/security/advisories/GHSA-jrr2-x33p-6hvc
- https://nvd.nist.gov/vuln/detail/CVE-2025-46342
- https://github.com/kyverno/kyverno/commit/3ff923b7756e1681daf73849954bd88516589194
- https://github.com/kyverno/kyverno
- https://pkg.go.dev/vuln/GO-2025-3652
