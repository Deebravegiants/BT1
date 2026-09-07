# [H] PraisonAI Vulnerable to Argument Injection into Cloud Run Environment Variables via Unsanitized Comma in gcloud --set-env-vars

## Summary
Severity: High
Advisory: GHSA-fvxx-ggmx-3cjg
CVE: CVE-2026-40113
CWE: CWE-88
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-fvxx-ggmx-3cjg
Type: github-advisory

## Affected
- PyPI: `PraisonAI` — affected >=0 <4.5.128

## Details
**Summary**

deploy.py constructs a single comma-delimited string for the gcloud run
deploy --set-env-vars argument by directly interpolating openai_model,
openai_key, and openai_base without validating that these values do not
contain commas. gcloud uses a comma as the key-value pair separator for
--set-env-vars. A comma in any of the three values causes gcloud to
parse the trailing text as additional KEY=VALUE definitions, injecting
arbitrary environment variables into the deployed Cloud Run service.


Grep Commands and Evidence

Step 1. Confirm the vulnerable string construction at line 150
```
    grep -n "set-env-vars\|openai_key\|openai_base\|openai_model" \
      src/praisonai/praisonai/deploy.py
```
    Expected output showing unsanitized interpolation:
    150:  '--set-env-vars', f'OPENAI_MODEL_NAME={openai_model},OPENAI_API_KEY={openai_key},OPENAI_API_BASE={openai_base}'

Step 2. Confirm no comma validation exists before this line
```
    grep -n "comma\|assertNotIn\|ValueError\|sanitize\|strip\|replace" \
      src/praisonai/praisonai/deploy.py
```
    Expected output: no results related to input validation

Step 3. View the full context of the vulnerable construction
```
    sed -n '140,165p' \
      src/praisonai/praisonai/deploy.py
```
    This block shows the gcloud command list where the three values are
    joined into one comma-separated string passed as a single argument
    element. gcloud receives this string and applies its own
    comma-based parsing, which the subprocess list form cannot prevent.

Step 4. Confirm subprocess is called without shell=True
```
    grep -n "subprocess\|Popen\|shell=" \
      src/praisonai/praisonai/deploy.py
```
    This confirms shell=False (default), meaning the injection is at the
    gcloud argument level, not the shell level. The comma delimiter is
    parsed by gcloud itself, not by /bin/sh.

Step 5. Confirm no existing advisory covers this file
```
    grep -rn "deploy.py\|set.env.vars\|openai_base" \
      src/praisonai/praisonai/deploy.py
```

Vulnerability Description

File:
  `src/praisonai/praisonai/deploy.py`

Vulnerable line:
```
  150: '--set-env-vars', f'OPENAI_MODEL_NAME={openai_model},OPENAI_API_KEY={openai_key},OPENAI_API_BASE={openai_base}'
```

The three values openai_model, openai_key, and openai_base originate
from environment variables or user-provided configuration and are
interpolated directly into a single f-string without validation.

The subprocess call uses a Python list without shell=True. This means
there is no shell injection. The subprocess module passes the f-string
as one complete argument to gcloud. gcloud then applies its own internal
parsing to the value of --set-env-vars using a comma as the delimiter.
This parsing is entirely outside Python's control.

If any of the three values contains a comma, gcloud splits on that comma
and creates an additional KEY=VALUE environment variable from the text
following it. There is no error or warning from gcloud when this occurs.

The three values are attacker-controllable in any scenario where
environment variables can be set before the deploy command runs. This
includes compromised dotenv files, poisoned CI pipeline secrets, and
local developer machines where an attacker has shell access.


Proof of Concept
```
 attacker-controlled openai_base value:

    export OPENAI_API_KEY="sk-legitimate-key"
    export OPENAI_MODEL_NAME="gpt-4"
    export OPENAI_API_BASE="https://api.openai.com/v1,INJECTED=attacker_value"
```

Run the deploy command. The string constructed at line 150 becomes:
```
    OPENAI_MODEL_NAME=gpt-4,OPENAI_API_KEY=sk-legitimate-key,OPENAI_API_BASE=https://api.openai.com/v1,INJECTED=attacker_value
```
gcloud parses this as four key-value pairs and creates all four as
environment variables in the Cloud Run service. INJECTED=attacker_value
is a real environment variable available to every request the service
handles.

Verify the injection after deployment:
```
    gcloud run services describe praisonai-service \
      --region us-central1 \
      --format "value(spec.template.spec.containers[0].env)"
```
The output includes INJECTED alongside the three legitimate variables.

API key override:

  `  export OPENAI_API_KEY="sk-real,OPENAI_API_KEY=sk-attacker"`

The constructed string contains OPENAI_API_KEY twice. In gcloud versions
where the last-defined value takes precedence, the deployed service uses
sk-attacker for all LLM API calls. All agent traffic routes through the
attacker-controlled API account.


**Impact**

An attacker who can influence any of the three environment variables
before deploy.py runs can inject arbitrary environment variables into
the deployed Cloud Run production service without triggering any error.

Injection scenarios include a malicious git hook that modifies a dotenv
file before deployment, a compromised CI pipeline secret, or any local
access that allows setting environment variables in the deploy shell
session.

Consequences include overriding the API key used by the production
service, injecting proxy settings that redirect all outbound LLM traffic,
setting debug or verbose flags that write sensitive data to Cloud Run
logs, and overriding any security-relevant variable the service reads
from its environment.

The API key override scenario is the highest-impact case. All production
LLM calls made by the deployed service are billed to and logged by the
attacker's API account, giving the attacker full visibility into every
agent prompt and response processed in production.


**Recommended Fix**

Pass each variable as a separate --update-env-vars flag so each value
is an isolated argument and gcloud never performs comma-based parsing
across multiple values:

    Before:
      ['gcloud', 'run', 'deploy', 'praisonai-service',
       '--set-env-vars',
       f'OPENAI_MODEL_NAME={openai_model},OPENAI_API_KEY={openai_key},OPENAI_API_BASE={openai_base}']

    After:
      ['gcloud', 'run', 'deploy', 'praisonai-service',
       '--update-env-vars', f'OPENAI_MODEL_NAME={openai_model}',
       '--update-env-vars', f'OPENAI_API_KEY={openai_key}',
       '--update-env-vars', f'OPENAI_API_BASE={openai_base}']

Each --update-env-vars element is a separate string in the subprocess
list. The subprocess module passes each as a distinct argument to
gcloud. gcloud receives three separate single-variable assignments and
performs no cross-argument comma parsing.

Add pre-flight validation as a secondary control:

    for label, value in [
        ("OPENAI_MODEL_NAME", openai_model),
        ("OPENAI_API_KEY", openai_key),
        ("OPENAI_API_BASE", openai_base),
    ]:
        if "," in value:
            raise ValueError(
                f"{label} contains a comma and would corrupt "
                f"--set-env-vars: {value!r}"
            )


References

CWE-88 Improper Neutralization of Argument Delimiters in a Command
gcloud run deploy documentation for --set-env-vars KEY=VALUE comma
delimiter specification

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-fvxx-ggmx-3cjg
- https://nvd.nist.gov/vuln/detail/CVE-2026-40113
- https://github.com/MervinPraison/PraisonAI
- https://github.com/MervinPraison/PraisonAI/releases/tag/v4.5.128
