# Q4034: privilege-escalation flag in inflateVersions

## Question
Can an unprivileged attacker reaching `staging/src/k8s.io/pod-security-admission/policy/registry.go` via create Pod or pod-template-bearing object subject to Pod Security Admission, supplying allowPrivilegeEscalation unset with a setuid-capable config, cause `inflateVersions` to be exercised such that the default/omitted allowPrivilegeEscalation is treated as compliant under the restricted profile, breaking the invariant that a Pod violating the enforced Pod Security level (privileged/host*/caps/runAsNonRoot) is rejected, and leading to Pod Security bypass -> privileged/host-access workload -> container escape / node compromise?

## Target
- File/function: `staging/src/k8s.io/pod-security-admission/policy/registry.go` -> `inflateVersions`
- Entrypoint: create Pod or pod-template-bearing object subject to Pod Security Admission
- Attacker controls: allowPrivilegeEscalation unset with a setuid-capable config
- Exploit idea: the default/omitted allowPrivilegeEscalation is treated as compliant under the restricted profile
- Invariant to test: a Pod violating the enforced Pod Security level (privileged/host*/caps/runAsNonRoot) is rejected
- Expected Immunefi impact: Pod Security bypass -> privileged/host-access workload -> container escape / node compromise
- Fast validation: table test with a crafted PodSpec through the policy check, assert a violation is reported
