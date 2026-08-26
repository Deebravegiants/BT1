# Q0258: case/enum bypass in CheckPrivileged

## Question
Can an unprivileged attacker reaching `staging/src/k8s.io/pod-security-admission/policy/check_privileged.go` via create Pod or pod-template-bearing object subject to Pod Security Admission, supplying a value using unexpected case, alias, or new enum for the restricted field, cause `CheckPrivileged` to be exercised such that the check's allowed-set comparison misses a variant, admitting a disallowed profile/capability, breaking the invariant that a Pod violating the enforced Pod Security level (privileged/host*/caps/runAsNonRoot) is rejected, and leading to Pod Security bypass -> privileged/host-access workload -> container escape / node compromise?

## Target
- File/function: `staging/src/k8s.io/pod-security-admission/policy/check_privileged.go` -> `CheckPrivileged`
- Entrypoint: create Pod or pod-template-bearing object subject to Pod Security Admission
- Attacker controls: a value using unexpected case, alias, or new enum for the restricted field
- Exploit idea: the check's allowed-set comparison misses a variant, admitting a disallowed profile/capability
- Invariant to test: a Pod violating the enforced Pod Security level (privileged/host*/caps/runAsNonRoot) is rejected
- Expected Immunefi impact: Pod Security bypass -> privileged/host-access workload -> container escape / node compromise
- Fast validation: table test with a crafted PodSpec through the policy check, assert a violation is reported
