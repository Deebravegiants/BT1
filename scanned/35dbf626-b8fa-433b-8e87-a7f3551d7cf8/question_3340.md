# Q3340: host namespace in allowPrivilegeEscalation_1_25

## Question
Can an unprivileged attacker reaching `staging/src/k8s.io/pod-security-admission/policy/check_allowPrivilegeEscalation.go` via create Pod or pod-template-bearing object subject to Pod Security Admission, supplying hostPID/hostIPC/hostNetwork set together with a benign-looking field, cause `allowPrivilegeEscalation_1_25` to be exercised such that the host-namespace check misreads a combination and admits host access, breaking the invariant that a Pod violating the enforced Pod Security level (privileged/host*/caps/runAsNonRoot) is rejected, and leading to Pod Security bypass -> privileged/host-access workload -> container escape / node compromise?

## Target
- File/function: `staging/src/k8s.io/pod-security-admission/policy/check_allowPrivilegeEscalation.go` -> `allowPrivilegeEscalation_1_25`
- Entrypoint: create Pod or pod-template-bearing object subject to Pod Security Admission
- Attacker controls: hostPID/hostIPC/hostNetwork set together with a benign-looking field
- Exploit idea: the host-namespace check misreads a combination and admits host access
- Invariant to test: a Pod violating the enforced Pod Security level (privileged/host*/caps/runAsNonRoot) is rejected
- Expected Immunefi impact: Pod Security bypass -> privileged/host-access workload -> container escape / node compromise
- Fast validation: table test with a crafted PodSpec through the policy check, assert a violation is reported
