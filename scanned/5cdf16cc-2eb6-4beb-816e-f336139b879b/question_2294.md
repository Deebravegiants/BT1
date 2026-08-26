# Q2294: capability add in ValidateConfiguration

## Question
Can an unprivileged attacker reaching `staging/src/k8s.io/pod-security-admission/admission/admission.go` via create Pod or pod-template-bearing object subject to Pod Security Admission, supplying a `capabilities.add` entry outside the restricted allow-list, cause `ValidateConfiguration` to be exercised such that capability normalization (case/prefix) lets a dangerous cap slip past the restricted check, breaking the invariant that a Pod violating the enforced Pod Security level (privileged/host*/caps/runAsNonRoot) is rejected, and leading to Pod Security bypass -> privileged/host-access workload -> container escape / node compromise?

## Target
- File/function: `staging/src/k8s.io/pod-security-admission/admission/admission.go` -> `ValidateConfiguration`
- Entrypoint: create Pod or pod-template-bearing object subject to Pod Security Admission
- Attacker controls: a `capabilities.add` entry outside the restricted allow-list
- Exploit idea: capability normalization (case/prefix) lets a dangerous cap slip past the restricted check
- Invariant to test: a Pod violating the enforced Pod Security level (privileged/host*/caps/runAsNonRoot) is rejected
- Expected Immunefi impact: Pod Security bypass -> privileged/host-access workload -> container escape / node compromise
- Fast validation: table test with a crafted PodSpec through the policy check, assert a violation is reported
