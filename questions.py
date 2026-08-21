import json
import os

from decouple import config

# todo: if scope_files is: 500 > 50, 300 > 30 , 100 > 10
MAX_REPO = 10
# todo: the GitLab namespace/project path, for example group/project
SOURCE_REPO = "worldcoin/orb-core"
# todo: the name of the repository
REPO_NAME = "orb-core"

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
    # Untrusted QR payloads, provisioning, and network input parsing
    # =================================================================================
    "src/plans/qr_scan/mod.rs",
    "src/plans/qr_scan/user.rs",
    "src/plans/qr_scan/operator.rs",
    "src/plans/qr_scan/wifi.rs",
    "src/agents/qr_code.rs",
    "src/network/mod.rs",
    "src/network/mecard.rs",
    "src/plans/wifi/mod.rs",
    "wpa-supplicant-interface/src/main.rs",
    "wpa-supplicant-interface/src/join.rs",
    "wpa-supplicant-interface/src/reconfigure.rs",
    "wpa-supplicant-interface/src/status.rs",
    "wpa-supplicant-interface/src/signal.rs",
    "orb-backend-connect/src/main.rs",

    # =================================================================================
    # Signup orchestration, session state, and enrollment authorization
    # =================================================================================
    "src/plans/mod.rs",
    "src/plans/enroll_user.rs",
    "src/plans/idle.rs",
    "src/plans/warmup.rs",
    "src/plans/detect_face.rs",
    "src/plans/health_check/mod.rs",
    "src/plans/health_check/ir_camera_fps.rs",
    "src/brokers/mod.rs",
    "src/brokers/orb.rs",
    "src/brokers/observer.rs",
    "src/bin/orb-core.rs",
    "src/lib.rs",
    "src/cli.rs",
    "src/ui/mod.rs",
    "src/sound.rs",

    # =================================================================================
    # Biometric capture, liveness, and fraud-signal enforcement
    # =================================================================================
    "src/plans/biometric_capture/mod.rs",
    "src/plans/biometric_capture/focus_sweep.rs",
    "src/plans/biometric_capture/mirror_sweep.rs",
    "src/plans/biometric_capture/multi_wavelength.rs",
    "src/plans/biometric_capture/overcapture.rs",
    "src/plans/biometric_capture/pupil_contraction.rs",
    "src/plans/biometric_pipeline/mod.rs",
    "src/plans/biometric_pipeline/code.rs",
    "src/plans/fraud_check.rs",
    "fraud-engine/src/lib.rs",
    "fraud-engine/src/dsl.rs",
    "fraud-engine/src/pipeline.rs",
    "fraud-engine/src/report.rs",
    "src/agents/eye_tracker.rs",
    "src/agents/eye_pid_controller.rs",
    "src/agents/distance.rs",
    "src/agents/mirror.rs",
    "src/agents/thermal.rs",
    "src/agents/ir_auto_exposure.rs",
    "src/agents/ir_auto_focus.rs",

    # =================================================================================
    # Model inference boundaries: iris, face, occlusion, and neural-net agents
    # =================================================================================
    "src/agents/python/mod.rs",
    "src/agents/python/iris/mod.rs",
    "src/agents/python/iris/types.rs",
    "src/agents/python/iris/extracts.rs",
    "src/agents/python/face_identifier/mod.rs",
    "src/agents/python/face_identifier/types.rs",
    "src/agents/python/occlusion.rs",
    "src/agents/python/ir_net.rs",
    "src/agents/python/rgb_net.rs",
    "src/agents/python/mega_agent_one.rs",
    "src/agents/python/mega_agent_two.rs",
    "ai-interface/src/lib.rs",
    "ir-net/src/lib.rs",
    "rgb-net/src/lib.rs",

    # =================================================================================
    # Identity binding, signing, custody packaging, and secret handling
    # =================================================================================
    "src/plans/personal_custody_package.rs",
    "src/secure_element.rs",
    "src/identification.rs",
    "src/short_lived_token.rs",
    "src/dbus.rs",
    "src/agents/image_notary.rs",
    "wld-data-id/src/lib.rs",
    "wld-data-id/src/wld_data_id.rs",
    "wld-data-id/src/s3_region.rs",

    # =================================================================================
    # Backend trust boundary: server-driven config, status, and upload endpoints
    # =================================================================================
    "src/backend/mod.rs",
    "src/backend/config.rs",
    "src/backend/endpoints.rs",
    "src/backend/signup_post.rs",
    "src/backend/signup_poll.rs",
    "src/backend/user_status.rs",
    "src/backend/operator_status.rs",
    "src/backend/orb_os_status.rs",
    "src/backend/status.rs",
    "src/backend/presigned_url.rs",
    "src/backend/s3_region.rs",
    "src/backend/upload_image.rs",
    "src/backend/upload_debug_report.rs",
    "src/backend/upload_personal_custody_package.rs",
    "src/config.rs",
    "src/calibration.rs",

    # =================================================================================
    # Data retention, uploads, telemetry, and serialization of captured biometrics
    # =================================================================================
    "src/agents/data_uploader.rs",
    "src/agents/image_uploader.rs",
    "src/debug_report.rs",
    "src/logger.rs",
    "src/ssd.rs",
    "src/process.rs",
    "src/image/mod.rs",
    "src/image/fisheye.rs",
    "src/utils/mod.rs",
    "src/utils/rkyv_ndarray.rs",
    "src/utils/serializable_instant.rs",
    "src/utils/serialize_with_sorted_keys.rs",

    # =================================================================================
    # Agent IPC, process isolation, and remote streaming surfaces
    # =================================================================================
    "agentwire/src/lib.rs",
    "agentwire/src/port.rs",
    "agentwire/src/agent/mod.rs",
    "agentwire/src/agent/process.rs",
    "agentwire/src/agent/task.rs",
    "agentwire/src/agent/thread.rs",
    "src/agents/mod.rs",
    "src/agents/livestream/mod.rs",
    "src/agents/livestream/upstream.rs",
    "src/agents/livestream/downstream.rs",
    "livestream-event/src/lib.rs",
    "orb-relay-client/src/lib.rs",
    "orb-relay-client/src/client.rs",
]


target_scopes = [
    "Critical. An unprivileged attacker standing in front of an Orb, controlling only a presented QR code (user, operator, or WiFi), the physical scene shown to the cameras, or their own signup session, can complete a signup bound to a user identity, signup ID, or data-policy that is not theirs.",
    "Critical. An unprivileged attacker can cause captured iris/face images, iris codes, or self-custody secrets to be encrypted to, uploaded to, or recoverable by an attacker-chosen key, URL, bucket, or session, leaking another person's biometric data.",
    "Critical. An unprivileged attacker can bypass or neutralize liveness, occlusion, fraud-check, or face/iris qualification enforcement so a presentation, replayed capture, or degraded-signal path is accepted as a genuine live human signup.",
    "Critical. An unprivileged attacker can forge, replay, or alter Orb-signed attestation material (secure-element signatures, iris-code commitments, signup payloads) so the backend accepts biometric data the Orb never captured or attributes it to the wrong user.",
    "High. An unprivileged attacker can force cross-signup state bleed, so one user's captured frames, iris codes, QR-derived identity, or fraud verdict is carried into another user's signup, upload, or custody package.",
    "High. An unprivileged attacker can use malformed QR, MECARD, backend-config, or agent-IPC input to crash, hang, or wedge the Orb signup state machine, or to inject attacker-controlled arguments into wpa_supplicant/child-process or upload calls.",
]


scope_scan = [
]


def question_generator(target_file: str) -> str:
    """
    Generate exploit-focused audit and fuzzing questions for one orb-core target.

    ```
    target_file format:
    "'File Name: src/plans/qr_scan/user.rs -> Scope: Critical. ...'"
    """

    prompt = f"""
    ```

    Generate exploit-focused security audit and fuzzing questions for this exact orb-core target:

    {target_file}

    Project focus:
    orb-core is the Rust software running on the Worldcoin Orb biometric imaging device. Focus on signup authorization and identity binding, QR-code parsing, biometric capture and liveness/fraud enforcement, iris-code and custody-package construction, secure-element signing, and upload/retention of biometric data.

    Rules:
    * Treat `File Name:` as the exact file/module.
    * Treat `Scope:` as the ONLY impact to target.
    * Assume full repo context is accessible.
    * Do not ask for code or say anything is missing.
    * Use exact Rust symbols (fn, struct, enum, field) when possible.
    * Attacker is unprivileged only: an ordinary person in front of the Orb or an ordinary backend API client. No operator/root/SSH access, no leaked keys or tokens, no hardware tampering, no firmware or MCU access, no malicious node/peer, no phishing, no social engineering.
    * Allowed attacker inputs are normal external surfaces: presented user/operator/WiFi QR payloads, the physical scene shown to the cameras (face, iris, distance, motion, temperature), the attacker's own signup session and identity, and API/backend responses reachable through that session.
    * Ignore test files, mocks, docs, generated files, build scripts, config-only findings, and dependency-only issues.
    * Do not rely on test-only cfg paths, mocked agents, or operator-only setup.
    * Generate 12 to 16 high-signal questions.
    * At least 70% must target signup authorization, identity/QR binding, liveness or fraud-check enforcement, biometric data disclosure, signing/attestation integrity, or cross-signup state bleed.
    * Every question must be testable by unit test, integration test, fuzz test, invariant test, or differential test.
    * Avoid generic checklist questions and repeated root causes.

    Core invariants:
    * Identity binding is exact: every captured frame, iris code, and uploaded package stays bound to the signup ID, user ID, data policy, and public key of the person actually scanned.
    * Biometric secrets stay contained: raw images, iris codes, and custody material must only be encrypted to the scanned user's key and sent to backend-authorized destinations, never persisted, logged, or reused beyond policy.
    * Liveness and fraud verdicts are fail-closed: missing, errored, timed-out, or default model signals must never be treated as a passing check.
    * Attestation is authentic: secure-element signatures and iris-code commitments must cover the exact serialized data captured in this session and must not be replayable across signups.
    * Sessions are isolated: aborting, timing out, or restarting a signup must fully reset capture, QR, and fraud state before the next user.
    * Untrusted parsed input never reaches process arguments, filesystem paths, URLs, or unbounded allocation.

    Each question must include:
    1. target function/module;
    2. attacker action;
    3. preconditions;
    4. call sequence;
    5. invariant tested;
    6. scoped impact;
    7. proof idea.

    Output only valid Python. No markdown. No explanations.

    questions = [
    "[File: {target_file}] [Function: symbol_or_module] Can an unprivileged ATTACKER_ACTION under PRECONDITIONS trigger CALL_SEQUENCE, violating INVARIANT, causing scoped impact: SCOPE_IMPACT? Proof idea: unit/integration/fuzz PARAMETERS and assert IDENTITY_BINDING, BIOMETRIC_CONTAINMENT, FRAUD_ENFORCEMENT, or ATTESTATION_INTEGRITY.",
    ]
    """
    return prompt


def audit_format(security_question: str) -> str:
    """
    Generate a focused orb-core exploit-validation prompt.
    """

    prompt = f"""# SECURITY AUDIT PROMPT

## Question
{security_question}

## Rules
- Use existing repo context only. Analyze only this question and scoped impact.
- Attacker is unprivileged only: no operator/root access, no leaked keys or tokens, no hardware or MCU tampering, no social engineering, no malicious node/peer assumptions.
- Reject anything that depends only on test/mock/config/docs/generated/build files, dependency bugs alone, test-only cfg paths, or best-practice cleanup without exploitable impact.
- Focus on real signup-compromise paths reachable from a presented QR code, the scene shown to the cameras, an attacker's own signup session, or backend responses within that session.

## Validate
- Trace the exact reachable Rust path from the attacker input into signup authorization, identity binding, capture/fraud enforcement, signing, or upload logic.
- Check whether existing validation, state resets, fraud checks, policy gates, or backend-side verification already stop it.
- Accept only real unauthorized signup, wrong-identity binding, biometric data disclosure, liveness/fraud bypass, attestation forgery, cross-signup state bleed, or signup-state wedge.
- Require exact file/function support and a reproducible unit/integration/fuzz/invariant PoC.

## Output
If valid, output exactly:

### Title
[Bug statement] - ([File: file_path])

### Summary
[2-3 sentences]

### Finding Description
[Code path, root cause, attacker inputs, exploit flow, and why checks fail]

### Impact Explanation
[Concrete scoped impact and matching Worldcoin/Orb bounty impact]

### Likelihood Explanation
[Preconditions, feasibility, repeatability]

### Recommendation
[Specific fix]

### Proof of Concept
[Unit/integration test or fuzz/invariant test plan with expected assertions]

If invalid, output exactly:
#NoVulnerability found for this question.

No extra text.
"""
    return prompt


def validation_format(report: str) -> str:
    """
    Generate a strict bounty-style validation prompt for orb-core security claims.
    """
    prompt = f"""# VALIDATION PROMPT

## Security Claim
{report}

## Rules
- Validate only the submitted claim.
- Check SECURITY.md and Researcher.Md for scope, exclusions, and valid impact classes.
- Do not create a new vulnerability if the submitted claim is weak or invalid.
- Do not upgrade severity unless the provided evidence proves the higher impact.
- Reject malicious-node, malicious-peer, operator-only, root/SSH, hardware- or MCU-tampering, physical-teardown, leaked-key, dependency-only, docs/style, generated-file, test/mock/config-only, and purely theoretical issues.
- Reject if the exploit needs victim social engineering, impossible setup, test-only cfg paths, or behavior outside normal Orb signup inputs.
- Reject if the bug was fixed, acknowledged, or publicly disclosed already, per the eligibility rules.
- A valid report must be triggerable by an unprivileged user in front of the Orb or an ordinary API client, unless the claim proves privilege escalation from an unprivileged path.
- The final impact must map to an in-scope Orb impact such as unauthorized or misattributed signup, biometric data disclosure, liveness/fraud-check bypass, attestation forgery, cross-signup state bleed, or unrecoverable signup-state failure.
- Prefer #NoVulnerability over speculative reports.

## Required Validation Checks
All must pass:
1. Exact in-scope file, function, and line/code references.
2. Clear root cause and broken security assumption.
3. Reachable exploit path: preconditions -> attacker action -> trigger -> bad result.
4. Existing checks/guards reviewed and shown insufficient.
5. Concrete in-scope impact with realistic likelihood.
6. Reproducible proof path: unit PoC, integration test, invariant/fuzz test, or exact manual steps at the Orb.
7. No obvious rejection reason from SECURITY.md, known issues, privilege assumptions, or scope exclusions.

## Silent Triage Questions
Before output, internally answer:
- Can a normal person in front of the Orb, or a normal API client, trigger this without privileged access?
- Does the code actually behave as claimed?
- Is the impact caused by this code, not by hardware access, operator privilege, backend-side policy, or a dependency alone?
- Is the identity, disclosure, bypass, or forgery impact concrete, not hypothetical?
- Would a bounty triager accept the proof?
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
[Concrete in-scope impact, severity rationale, and bounty category]

## Likelihood Explanation
[Attacker capability, required conditions, feasibility, repeatability]

## Recommendation
[Specific fix guidance]

## Proof of Concept
[Minimal reproducible steps or fuzz/invariant/integration test plan]

If invalid, output exactly:
#NoVulnerability found for this question.

Output only one of the two outcomes above. No extra text.
"""
    return prompt


def scan_format(report: str) -> str:
    """
    Generate a short cross-project analog scan prompt for orb-core.
    """
    prompt = f"""# ANALOG SCAN PROMPT

## External Report
{report}

## Rules
- Use in-scope production repo context only. Do not ask for code or claim missing files.
- Use the external report only as a bug-class hint, not as proof.
- Keep only unprivileged-user analogs in QR/MECARD parsing, signup authorization, identity binding, liveness/fraud enforcement, biometric upload and retention, secure-element signing, or agent-IPC trust boundaries.
- Reject malicious-node/peer/operator analogs, hardware-access analogs, test-only paths, dependency-only bugs, and no-impact analogs.

## Validate
- Map the bug class to the strongest reachable orb-core path.
- Prove root cause with exact file/function support.
- Accept only concrete unauthorized or misattributed signup, biometric data disclosure, fraud/liveness bypass, attestation forgery, or cross-signup state bleed impact.

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
