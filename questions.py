import json
import os

from decouple import config

# todo: if scope_files is: 500 > 50, 300 > 30 , 100 > 10
MAX_REPO = 20
# todo: the GitLab namespace/project path, for example group/project
SOURCE_REPO = 'kubernetes/kubernetes'
# todo: the name of the repository
REPO_NAME = 'kubernetes'

run_number = os.environ.get('GITHUB_RUN_NUMBER', '0')


def get_cyclic_index(run_number, max_index=100):
    """Convert run number to a cyclic index between 1 and max_index"""
    return (int(run_number) - 1) % max_index + 1


def load_repository_urls():
    """Load repository URLs from repositories.json."""
    repo_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "repositories.json")
    if not os.path.exists(repo_file):
        return []

    try:
        with open(repo_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return []

    if not isinstance(data, list):
        return []

    return [url for url in data if isinstance(url, str) and url.strip()]


if run_number == "0":
    BASE_URL = f"https://deepwiki.com/{SOURCE_REPO}"
else:
    repository_urls = load_repository_urls()
    if repository_urls:
        run_index = get_cyclic_index(run_number, len(repository_urls))
        BASE_URL = repository_urls[run_index - 1]
    else:
        BASE_URL = f"https://deepwiki.com/{SOURCE_REPO}"

scope_files = [
    # =================================================================================
    # Authorization: RBAC evaluation and node authorizer reachable from any request
    # =================================================================================
    "plugin/pkg/auth/authorizer/rbac/rbac.go",
    "plugin/pkg/auth/authorizer/rbac/subject_locator.go",
    "pkg/registry/rbac/validation/rule.go",
    "pkg/registry/rbac/validation/policy_compact.go",
    "plugin/pkg/auth/authorizer/node/node_authorizer.go",
    "plugin/pkg/auth/authorizer/node/graph.go",
    "plugin/pkg/auth/authorizer/node/graph_populator.go",
    "staging/src/k8s.io/apiserver/pkg/authorization/authorizer/rule.go",
    "staging/src/k8s.io/apiserver/pkg/authorization/authorizer/evaluate.go",
    "staging/src/k8s.io/apiserver/pkg/authorization/union/union.go",
    "staging/src/k8s.io/apiserver/pkg/authorization/path/path.go",

    # =================================================================================
    # RBAC privilege-escalation guards: bind/escalate protection on roles and bindings
    # =================================================================================
    "pkg/registry/rbac/escalation_check.go",
    "pkg/registry/rbac/helpers.go",
    "pkg/registry/rbac/role/policybased/storage.go",
    "pkg/registry/rbac/rolebinding/policybased/storage.go",
    "pkg/registry/rbac/clusterrole/policybased/storage.go",
    "pkg/registry/rbac/clusterrolebinding/policybased/storage.go",
    "pkg/registry/authorization/util/helpers.go",
    "pkg/registry/authorization/subjectaccessreview/rest.go",
    "pkg/registry/authorization/localsubjectaccessreview/rest.go",

    # =================================================================================
    # Authentication: token/cert request paths an unprivileged caller controls
    # =================================================================================
    "staging/src/k8s.io/apiserver/pkg/authentication/request/bearertoken/bearertoken.go",
    "staging/src/k8s.io/apiserver/pkg/authentication/request/union/union.go",
    "staging/src/k8s.io/apiserver/pkg/authentication/request/x509/x509.go",
    "staging/src/k8s.io/apiserver/pkg/authentication/request/x509/verify_options.go",
    "staging/src/k8s.io/apiserver/pkg/authentication/request/anonymous/anonymous.go",
    "staging/src/k8s.io/apiserver/pkg/authentication/token/jwt/jwt.go",
    "staging/src/k8s.io/apiserver/pkg/authentication/token/union/union.go",
    "staging/src/k8s.io/apiserver/pkg/authentication/serviceaccount/util.go",

    # =================================================================================
    # ServiceAccount token issuance, claims and validation
    # =================================================================================
    "pkg/serviceaccount/jwt.go",
    "pkg/serviceaccount/claims.go",
    "pkg/serviceaccount/legacy.go",

    # =================================================================================
    # Admission: identity, isolation and escalation controls on write requests
    # =================================================================================
    "plugin/pkg/admission/serviceaccount/admission.go",
    "plugin/pkg/admission/noderestriction/admission.go",
    "plugin/pkg/admission/nodetaint/admission.go",
    "plugin/pkg/admission/security/podsecurity/admission.go",
    "plugin/pkg/admission/certificates/approval/admission.go",
    "plugin/pkg/admission/certificates/signing/admission.go",
    "plugin/pkg/admission/certificates/subjectrestriction/admission.go",
    "plugin/pkg/admission/priority/admission.go",
    "plugin/pkg/admission/gc/gc_admission.go",
    "plugin/pkg/admission/podtolerationrestriction/admission.go",
    "plugin/pkg/admission/podnodeselector/admission.go",
    "plugin/pkg/admission/limitranger/admission.go",
    "staging/src/k8s.io/apiserver/pkg/admission/plugin/resourcequota/controller.go",

    # =================================================================================
    # Pod Security Admission: policy checks that gate privileged/host access
    # =================================================================================
    "staging/src/k8s.io/pod-security-admission/admission/admission.go",
    "staging/src/k8s.io/pod-security-admission/admission/pods.go",
    "staging/src/k8s.io/pod-security-admission/policy/registry.go",
    "staging/src/k8s.io/pod-security-admission/policy/check_privileged.go",
    "staging/src/k8s.io/pod-security-admission/policy/check_hostNamespaces.go",
    "staging/src/k8s.io/pod-security-admission/policy/check_hostPathVolumes.go",
    "staging/src/k8s.io/pod-security-admission/policy/check_capabilities_restricted.go",
    "staging/src/k8s.io/pod-security-admission/policy/check_allowPrivilegeEscalation.go",
    "staging/src/k8s.io/pod-security-admission/policy/check_runAsNonRoot.go",
    "staging/src/k8s.io/pod-security-admission/policy/check_seccompProfile_restricted.go",
    "staging/src/k8s.io/pod-security-admission/policy/helpers.go",

    # =================================================================================
    # Core API validation and security-context accessors on user-submitted specs
    # =================================================================================
    "pkg/apis/core/validation/validation.go",
    "pkg/apis/core/validation/names.go",
    "pkg/securitycontext/accessors.go",
    "pkg/securitycontext/util.go",

    # =================================================================================
    # Request handlers: create/update/patch pipeline reachable via public API
    # =================================================================================
    "staging/src/k8s.io/apiserver/pkg/endpoints/handlers/create.go",
    "staging/src/k8s.io/apiserver/pkg/endpoints/handlers/update.go",
    "staging/src/k8s.io/apiserver/pkg/endpoints/handlers/patch.go",
    "staging/src/k8s.io/apiserver/pkg/endpoints/handlers/rest.go",
    "staging/src/k8s.io/apiserver/pkg/endpoints/handlers/namer.go",
]


target_scopes = [
    "Critical. An unprivileged authenticated user escalates their own privileges by creating or binding a Role, ClusterRole, RoleBinding, or ClusterRoleBinding that grants permissions they do not already hold, bypassing the escalation and bind checks in escalation_check.go or the policybased storage wrappers, reaching cluster-admin or cross-namespace control.",
    "Critical. An unprivileged user gains access to a resource, verb, namespace, or resource name their RBAC rules do not cover through a flaw in rule matching, wildcard/subresource handling, or authorizer union evaluation, obtaining unauthorized read or write across tenants.",
    "Critical. An unprivileged user authenticates as another identity or with elevated group membership by forging, confusing, or replaying a bearer or serviceaccount JWT, exploiting token validation, claim parsing, audience/expiry handling, or authenticator union ordering.",
    "Critical. An unprivileged user submits a Pod (or pod-template controller object) that passes Pod Security Admission yet runs privileged, hostPID/hostIPC/hostNetwork, hostPath, or with escalated capabilities, achieving node compromise or container escape via a policy-check bypass.",
    "Critical. An unprivileged user obtains or projects a serviceaccount token, or binds a workload to a serviceaccount, they do not control by exploiting the serviceaccount admission mount logic, token claims, or bound-object validation, gaining that account's API privileges.",
    "Critical. An unprivileged user reads or mutates objects in another namespace or another tenant's scope by exploiting name/namespace resolution, self/local subject access review, or request-handler namer confusion so authorization is evaluated against the wrong scope.",
    "High. An unprivileged user gets a CertificateSigningRequest approved or signed for a username, group, or node identity they are not entitled to, bypassing the certificate approval, signing, or subject-restriction admission controllers, yielding a forged client identity.",
    "High. An unprivileged user bypasses the NodeRestriction or serviceaccount admission controllers to set nodeName, serviceAccountName, tolerations, or node/pod status fields they must not control, escaping workload isolation or impersonating node-scoped access.",
    "High. An unprivileged user smuggles a malformed or under-validated field through core API validation (validation.go, names.go, securitycontext accessors) so an invalid spec is persisted, injecting into a downstream consumer or corrupting another user's object.",
    "High. An unprivileged user bypasses priority, ResourceQuota, LimitRange, or garbage-collection admission to assign a system PriorityClass, exceed quota, or delete/adopt objects owned by others via crafted ownerReferences, denying service or seizing resources.",
]


scope_scan = [
]


def question_generator(target_file: str) -> str:
    """
    Generate exploit-focused audit and fuzzing questions for one kubernetes target.

    ```
    target_file format:
    "'File Name: plugin/pkg/auth/authorizer/rbac/rbac.go -> Scope: Critical. ...'"
    """

    prompt = f"""
    ```

    Generate exploit-focused security audit questions for this exact kubernetes target:

    {target_file}

    Project focus:
    kubernetes is the reference Kubernetes control-plane. Focus on kube-apiserver request handling reachable by an ordinary authenticated user: authentication and token validation, RBAC and node authorization, RBAC privilege-escalation guards, admission controllers (serviceaccount, noderestriction, certificates, priority, gc, resourcequota), Pod Security Admission, serviceaccount token issuance, and core API object validation.

    Rules:
    * Treat `File Name:` as the exact file/package.
    * Treat `Scope:` as the ONLY impact to target.
    * Assume full repo context is accessible.
    * Do not ask for code or say anything is missing.
    * Use exact Go symbols (func, method, struct, field) when possible.
    * Attacker is unprivileged only: an ordinary authenticated user or serviceaccount with minimal, namespace-scoped RBAC. They can call the public kube-apiserver, create/update/patch objects they are allowed, submit CSRs and SubjectAccessReviews, and run their own pods where permitted.
    * Attacker is NOT a cluster-admin, node/kubelet, controller-manager, scheduler, etcd operator, or webhook operator. Ignore malicious-node, malicious-peer, network-layer, kubelet-host, CLI, misconfiguration, leaked-credential, and social-engineering assumptions.
    * Ignore test files, mocks, fuzz harnesses, docs, generated (zz_generated, deepcopy, conversion) files, config-only findings, and dependency-only issues.
    * Ignore issues gated behind alpha feature gates that are off by default unless the path is reachable on default configuration.
    * Generate 30 to 40 high-signal questions.
    * At least 70% must target privilege escalation, RBAC or authorizer bypass, authentication/token forgery, admission or Pod Security bypass, serviceaccount token/identity confusion, cross-namespace access, or CSR identity forgery.
    * Every question must be testable by unit test, integration test, or table/differential test against apiserver logic.
    * Avoid generic checklist questions and repeated root causes.

    Core invariants:
    * Authorization is exact: a user only gets verbs/resources/names/namespaces their bound RBAC or node scope allows; escalation and bind checks block granting rights the requester lacks.
    * Authentication is sound: only a validly issued, unexpired, correctly-audienced token or client cert authenticates, and identity/groups cannot be forged or confused.
    * Isolation holds: serviceaccount, noderestriction, and namespace boundaries prevent acting as another identity, node, or tenant.
    * Admission is complete: Pod Security and admission controllers cannot be bypassed to run privileged/host-access workloads or set protected fields.
    * Validation is total: user-submitted specs are fully validated before persistence; no malformed field is stored or smuggled downstream.

    Each question must include:
    1. target function/method;
    2. attacker action (a concrete API request);
    3. preconditions (the minimal RBAC held);
    4. request sequence;
    5. invariant tested;
    6. scoped impact;
    7. proof idea.

    Output only valid Python. No markdown. No explanations.

    questions = [
    "[File: {target_file}] [Function: symbol_or_method] Can an unprivileged ATTACKER_ACTION under PRECONDITIONS trigger REQUEST_SEQUENCE, violating INVARIANT, causing scoped impact: SCOPE_IMPACT? Proof idea: unit/integration test PARAMETERS and assert AUTHORIZATION_EXACTNESS, AUTHENTICATION_SOUNDNESS, ISOLATION, ADMISSION_COMPLETENESS, or VALIDATION_TOTALITY.",
    ]
    """
    return prompt


def audit_format(security_question: str) -> str:
    """
    Generate a focused kubernetes exploit-validation prompt.
    """

    prompt = f"""# SECURITY AUDIT PROMPT

## Question
{security_question}

## Rules
- Use existing repo context only. Analyze only this question and scoped impact.
- Attacker is unprivileged only: an ordinary authenticated user or serviceaccount with minimal namespace-scoped RBAC, calling the public kube-apiserver. No cluster-admin, node/kubelet, controller, scheduler, etcd, or webhook-operator access; no leaked credentials or social engineering.
- Reject malicious-node, malicious-kubelet, network-layer, host-level, operator-only, and misconfiguration-only paths.
- Reject anything depending only on test/mock/fuzz/docs/config/generated files, dependency bugs alone, or best-practice cleanup without exploitable impact.
- Focus on real control-plane compromise: privilege escalation, RBAC or authorizer bypass, authentication/token forgery, admission or Pod Security bypass, serviceaccount/identity confusion, cross-namespace access, or CSR identity forgery.

## Validate
- Trace the exact reachable path from the attacker's API request (create/update/patch, CSR, token, SubjectAccessReview, pod spec) into the affected function.
- Check whether existing authorization, escalation/bind checks, admission, validation, or feature-gate defaults already stop it.
- Accept only real privilege escalation, unauthorized cross-tenant read/write, identity forgery, workload isolation escape, or a persisted invalid/protected field.
- Require exact file/function support and a reproducible unit/integration/table test PoC.

## Output
If valid, output exactly:

### Title
[Bug statement] - ([File: file_path])

### Summary
[2-3 sentences]

### Finding Description
[Code path, root cause, attacker request inputs, exploit flow, and why checks fail]

### Impact Explanation
[Concrete scoped impact and matching Kubernetes bounty impact class]

### Likelihood Explanation
[Preconditions, minimal RBAC needed, feasibility, repeatability]

### Recommendation
[Specific fix]

### Proof of Concept
[Unit/integration/table test plan with expected assertions]

If invalid, output exactly:
#NoVulnerability found for this question.

No extra text.
"""
    return prompt


def validation_format(report: str) -> str:
    """
    Generate a strict bounty-style validation prompt for kubernetes security claims.
    """
    prompt = f"""# VALIDATION PROMPT

## Security Claim
{report}

## Rules
- Validate only the submitted claim.
- Check SECURITY.md and Researcher.Md for scope, exclusions, and valid impact classes.
- Do not create a new vulnerability if the submitted claim is weak or invalid.
- Do not upgrade severity unless the provided evidence proves the higher impact.
- Reject malicious-node, malicious-kubelet, network-layer, host-level, operator-only, misconfiguration, leaked-credential, dependency-only, docs/style, generated-file, and test/mock/config-only issues.
- Reject if the exploit needs cluster-admin, node, controller, or webhook privileges, victim social engineering, an impossible setup, or behavior outside what an ordinary authenticated user can submit to the public kube-apiserver.
- Reject if the bug was fixed, acknowledged, or publicly disclosed already, per the eligibility rules.
- A valid report must be triggerable by an unprivileged authenticated user, unless the claim proves privilege escalation from an unprivileged starting point.
- The final impact must map to an in-scope Kubernetes impact such as privilege escalation, RBAC/authorization bypass, authentication or token forgery, admission or Pod Security bypass enabling privileged/host workloads, serviceaccount identity confusion, cross-namespace/tenant data access, or CSR identity forgery.
- Prefer #NoVulnerability over speculative reports.

## Required Validation Checks
All must pass:
1. Exact in-scope file, function, and line/code references.
2. Clear root cause and broken security assumption.
3. Reachable exploit path: preconditions (minimal RBAC) -> attacker API request -> trigger -> bad result.
4. Existing authorization, escalation/bind checks, admission, and validation reviewed and shown insufficient.
5. Concrete in-scope impact with realistic likelihood.
6. Reproducible proof path: unit PoC, integration test, table/differential test, or exact kubectl/API steps against a local cluster.
7. No obvious rejection reason from SECURITY.md, known issues, privilege assumptions, or scope exclusions.

## Silent Triage Questions
Before output, internally answer:
- Can an ordinary authenticated user trigger this through normal API requests without cluster-admin, node, or controller access?
- Does the code actually behave as claimed on default feature-gate configuration?
- Is the impact caused by this code, not by a malicious node, controller, or dependency alone?
- Is the escalation, bypass, forgery, or cross-tenant access concrete, not hypothetical?
- Would a Kubernetes bounty triager accept the proof?
- What exact test would prove it?

## Output
If valid, output exactly:

Audit Report

## Title
[Clear vulnerability statement] - ([File: file_path])

## Summary
[2-3 sentence summary of the bug and impact]

## Finding Description
[Exact code path, root cause, exploit flow, and why existing checks fail]

## Impact Explanation
[Concrete in-scope impact, severity rationale, and Kubernetes bounty category]

## Likelihood Explanation
[Attacker capability, required RBAC, feasibility, repeatability]

## Recommendation
[Specific fix guidance]

## Proof of Concept
[Minimal reproducible steps or integration/table/unit test plan]

If invalid, output exactly:
#NoVulnerability found for this question.

Output only one of the two outcomes above. No extra text.
"""
    return prompt


def scan_format(report: str) -> str:
    """
    Generate a short cross-project analog scan prompt for kubernetes.
    """
    prompt = f"""# ANALOG SCAN PROMPT

## External Report
{report}

## Rules
- Use in-scope production repo context only. Do not ask for code or claim missing files.
- Use the external report only as a bug-class hint, not as proof.
- Keep only unprivileged-user analogs in authentication/token validation, RBAC and node authorization, RBAC escalation guards, admission controllers, Pod Security Admission, serviceaccount token issuance, or core API validation.
- Reject malicious-node, malicious-kubelet, network-layer, operator-only, mocked-only paths, dependency-only bugs, and no-impact analogs.

## Validate
- Map the bug class to the strongest reachable kubernetes path from an ordinary authenticated user's API request.
- Prove root cause with exact file/function support.
- Accept only concrete privilege escalation, RBAC/authorization bypass, authentication or token forgery, admission or Pod Security bypass, serviceaccount identity confusion, cross-namespace access, or CSR identity forgery.

## Output (Strict)
If valid analog exists, output:

### Title
[Clear vulnerability statement] - ([File: file_path])

### Summary
### Finding Description
### Impact Explanation
### Likelihood Explanation
### Recommendation
### Proof of Concept

If not, output exactly:
#NoVulnerability found for this question.

No extra text.
"""
    return prompt
