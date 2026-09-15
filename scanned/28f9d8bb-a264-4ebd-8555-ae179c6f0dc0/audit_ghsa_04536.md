# [M] Bleach clean() / Cleaner() fails to sanitize dangerous URI schemes in allowed formaction attributes

## Summary
Severity: Medium
Advisory: GHSA-gj48-438w-jh9v
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-gj48-438w-jh9v
Type: github-advisory

## Affected
- PyPI: `bleach` — affected >=0 <6.4.0

## Details
### Summary

Bleach `clean()` / `Cleaner()` fails to sanitize dangerous URI schemes in allowed `formaction` attributes.

Bleach applies URI protocol sanitization only to attributes listed in `attr_val_is_uri`. While URI-bearing attributes such as `action`, `href`, `src`, and `poster` are included in that set, `formaction` is not. As a result, if a downstream application explicitly allows `formaction` on submit-capable controls in untrusted HTML, Bleach preserves dangerous values such as `javascript:alert(1)` instead of stripping them.

This can lead to **submit-triggered JavaScript execution** in applications that rely on Bleach to sanitize untrusted HTML and allow the relevant tag/attribute combination.

---

### Details

The issue appears to be a URI-sanitization coverage gap in Bleach’s sanitizer logic.

Relevant code paths:

* `bleach/sanitizer.py` — `BleachSanitizerFilter.allow_token` (around line 553)
* `bleach/_vendor/html5lib/filters/sanitizer.py` — `attr_val_is_uri` (around line 525)

In `BleachSanitizerFilter.allow_token`, URI protocol sanitization is only applied when:

```python id="pft79m"
if namespaced_name in self.attr_val_is_uri:
```

However, `(None, 'formaction')` is currently missing from `attr_val_is_uri`.

This creates an inconsistency where `action` is protocol-sanitized, but `formaction` is not.

As a result, if a downstream application allows:

* tags such as `<button>` or `<input>`
* the `formaction` attribute

then Bleach preserves dangerous URI schemes such as `javascript:` in `formaction`.

Examples of affected submit-capable controls include:

* `<button>` (default submit behavior unless `type="button"` is set)
* `<input type="submit">`
* `<input type="image">`

This appears to be a real library-side sanitizer gap rather than only an application misuse issue, because Bleach already treats similar URI-bearing attributes (such as `action`) as protocol-sensitive and sanitizes them.

Suggested minimal fix:

Add:

```python id="4v4fkn"
(None, 'formaction')
```

to `attr_val_is_uri` in:

* `bleach/_vendor/html5lib/filters/sanitizer.py`

I also prepared a minimal patch and focused regression tests if helpful.

---

### PoC

Below are minimal reproductions using `bleach.clean()`.

#### 1) `<button>`

```python id="d3g0v7"
from bleach import clean

print(clean(
    '<form><button formaction="javascript:alert(1)">go</button></form>',
    tags={'form', 'button'},
    attributes={'button': ['formaction']},
))
```

**Actual output:**

```html id="i4nd7s"
<form><button formaction="javascript:alert(1)">go</button></form>
```

**Expected output:**

```html id="g4d2r1"
<form><button>go</button></form>
```

---

#### 2) `<input type="submit">`

```python id="l4dy0j"
print(clean(
    '<form><input type="submit" formaction="javascript:alert(1)" value="go"></form>',
    tags={'form', 'input'},
    attributes={'input': ['type', 'formaction', 'value']},
))
```

**Actual output:**

```html id="h8lgbt"
<form><input type="submit" formaction="javascript:alert(1)" value="go"></form>
```

**Expected output:**

```html id="6y8mws"
<form><input type="submit" value="go"></form>
```

---

#### 3) `<input type="image">`

```python id="g8q0x8"
print(clean(
    '<form><input type="image" formaction="javascript:alert(1)" src="/foo.png"></form>',
    tags={'form', 'input'},
    attributes={'input': ['type', 'formaction', 'src']},
))
```

**Actual output:**

```html id="fd22kg"
<form><input type="image" formaction="javascript:alert(1)" src="/foo.png"></form>
```

**Expected output:**

```html id="z6t6je"
<form><input type="image" src="/foo.png"></form>
```

---

### Impact

This is a **client-side HTML sanitization bypass / dangerous URI preservation issue**.

If an application relies on Bleach to sanitize untrusted HTML and explicitly allows:

* `formaction`
* and submit-capable controls such as `<button>` or `<input>`

then Bleach can emit sanitized output that still contains a dangerous `javascript:` URI in `formaction`.

That can lead to **submit-triggered JavaScript execution** when the user activates the control.

Impact is limited to configurations that explicitly allow the relevant tag/attribute combination, but the issue is still security-relevant because:

* `formaction` is a real browser sink
* Bleach already protocol-sanitizes similar URI-bearing attributes like `action`
* the omission creates inconsistent sanitizer coverage for dangerous URI schemes

I would currently assess this as **Medium severity**.

If useful, I also have:

* a minimal patch
* focused regression tests for:

  * `<button formaction="javascript:...">`
  * `<input type="submit" formaction="javascript:...">`
  * `<input type="image" formaction="javascript:...">`
  * a safe control case where `formaction="/submit"` is preserved

## References
- https://github.com/mozilla/bleach/security/advisories/GHSA-gj48-438w-jh9v
- https://github.com/mozilla/bleach
- https://github.com/mozilla/bleach/releases/tag/v6.4.0
