# Q3737: field omission in exemptNamespaceWarning

## Question
Can an unprivileged attacker reaching `staging/src/k8s.io/pod-security-admission/admission/admission.go` via create Pod or pod-template-bearing object subject to Pod Security Admission, supplying a Pod that omits a securityContext field the check keys on, cause `exemptNamespaceWarning` to be exercised such that the policy check treats a nil/omitted field as compliant, admitting a privileged/host capability, breaking the invariant that a Pod violating the enforced Pod Security level (privileged/host*/caps/runAsNonRoot) is rejected, and leading to Pod Security bypass -> privileged/host-access workload -> container escape / node compromise?

## Target
- File/function: `staging/src/k8s.io/pod-security-admission/admission/admission.go` -> `exemptNamespaceWarning`
- Entrypoint: create Pod or pod-template-bearing object subject to Pod Security Admission
- Attacker controls: a Pod that omits a securityContext field the check keys on
- Exploit idea: the policy check treats a nil/omitted field as compliant, admitting a privileged/host capability
- Invariant to test: a Pod violating the enforced Pod Security level (privileged/host*/caps/runAsNonRoot) is rejected
- Expected Immunefi impact: Pod Security bypass -> privileged/host-access workload -> container escape / node compromise
- Fast validation: table test with a crafted PodSpec through the policy check, assert a violation is reported
