# Q2724: container-type gap in ValidatePod

## Question
Can an unprivileged attacker reaching `staging/src/k8s.io/pod-security-admission/admission/admission.go` via create Pod or pod-template-bearing object subject to Pod Security Admission, supplying a setting placed only on an initContainer / ephemeralContainer, cause `ValidatePod` to be exercised such that the check visits only regular containers, missing a privileged init/ephemeral container, breaking the invariant that a Pod violating the enforced Pod Security level (privileged/host*/caps/runAsNonRoot) is rejected, and leading to Pod Security bypass -> privileged/host-access workload -> container escape / node compromise?

## Target
- File/function: `staging/src/k8s.io/pod-security-admission/admission/admission.go` -> `ValidatePod`
- Entrypoint: create Pod or pod-template-bearing object subject to Pod Security Admission
- Attacker controls: a setting placed only on an initContainer / ephemeralContainer
- Exploit idea: the check visits only regular containers, missing a privileged init/ephemeral container
- Invariant to test: a Pod violating the enforced Pod Security level (privileged/host*/caps/runAsNonRoot) is rejected
- Expected Immunefi impact: Pod Security bypass -> privileged/host-access workload -> container escape / node compromise
- Fast validation: table test with a crafted PodSpec through the policy check, assert a violation is reported
