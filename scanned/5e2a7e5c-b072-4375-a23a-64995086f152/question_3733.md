# Q3733: volume type in exemptNamespace

## Question
Can an unprivileged attacker reaching `staging/src/k8s.io/pod-security-admission/admission/admission.go` via create Pod or pod-template-bearing object subject to Pod Security Admission, supplying a hostPath or other restricted volume disguised via projected/ephemeral wrapper, cause `exemptNamespace` to be exercised such that the restricted-volume check misclassifies a wrapper volume, admitting host filesystem access, breaking the invariant that a Pod violating the enforced Pod Security level (privileged/host*/caps/runAsNonRoot) is rejected, and leading to Pod Security bypass -> privileged/host-access workload -> container escape / node compromise?

## Target
- File/function: `staging/src/k8s.io/pod-security-admission/admission/admission.go` -> `exemptNamespace`
- Entrypoint: create Pod or pod-template-bearing object subject to Pod Security Admission
- Attacker controls: a hostPath or other restricted volume disguised via projected/ephemeral wrapper
- Exploit idea: the restricted-volume check misclassifies a wrapper volume, admitting host filesystem access
- Invariant to test: a Pod violating the enforced Pod Security level (privileged/host*/caps/runAsNonRoot) is rejected
- Expected Immunefi impact: Pod Security bypass -> privileged/host-access workload -> container escape / node compromise
- Fast validation: table test with a crafted PodSpec through the policy check, assert a violation is reported
