# [M] Excelize: Negative shared-string index causes panic in GetCellValue and GetRows

## Summary
Severity: Medium
Advisory: GHSA-fx5j-qcqg-grpf
Aliases: CVE-2026-59162
Ecosystem: Go
Published: 2026-09-10
Source: https://osv.dev/vulnerability/GHSA-fx5j-qcqg-grpf
Type: osv

## Affected
- Go: `github.com/xuri/excelize/v2` — affected >=0 <2.11.0
- Go: `github.com/xuri/excelize` — affected unspecified

## Details
# Negative shared-string index causes panic in GetCellValue and GetRows

## Summary

Excelize parses shared-string cell values with `strconv.Atoi` and checks only the upper bound before indexing the shared string slice. If an XLSX file contains a shared-string cell with `<v>-1</v>`, the parsed index is negative. The upper-bound check still passes (`len(sharedStrings) > -1`), and Excelize indexes `sharedStrings[-1]`, causing a runtime panic.

This was reproduced on the current default branch commit `1213a8bd7c5ab360554603ac5c995ccaf6eb4314` and the latest release tag `v2.10.1` (`5ad5ab3af0054c55bdce09f1530085600e9f2e45`). The issue is independent from the row-bound allocation report, so I am reporting it separately.

## Affected package

- Package: `github.com/xuri/excelize/v2`
- Tested affected versions: current default branch at `1213a8bd7c5ab360554603ac5c995ccaf6eb4314`, and release `v2.10.1`
- Fixed version: none known at the time of this report

## Impact

An attacker who can provide an XLSX file to an application using Excelize can trigger a process panic when the application reads the malicious cell through common APIs such as `GetCellValue` or `GetRows`. In services that parse untrusted spreadsheets without a panic recovery boundary, this can cause denial of service.

## Root cause

For shared-string cells (`t="s"`), `xlsxC.getValueFrom()` parses the cell value as a shared-string index and only checks whether the index is below `len(d.SI)` before indexing:

```go
xlsxSI, _ := strconv.Atoi(strings.TrimSpace(c.V))
if len(d.SI) > xlsxSI {
    return d.SI[xlsxSI].String(), nil
}
```

For `xlsxSI == -1`, `len(d.SI) > -1` is true, so the code proceeds to index `d.SI[-1]` and panics.

## Minimal worksheet payload

```xml
<?xml version="1.0" encoding="UTF-8"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <sheetData>
    <row r="1"><c r="A1" t="s"><v>-1</v></c></row>
  </sheetData>
</worksheet>
```

The workbook also contains a normal `sharedStrings.xml` with one string (`ok`), so the failure is specifically due to accepting a negative index.

## Reproduction

Calling `GetCellValue("Sheet1", "A1")` on the workbook panics:

```text
== negative shared string GetCellValue ==
elapsed=0s alloc_delta=0MB
PANIC: runtime.boundsError runtime error: index out of range [-1]
```

Calling `GetRows("Sheet1")` on the same workbook also panics:

```text
== negative shared string GetRows ==
elapsed=0s alloc_delta=0MB
PANIC: runtime.boundsError runtime error: index out of range [-1]
```

The same results were observed on current default branch commit `1213a8bd7c5ab360554603ac5c995ccaf6eb4314` and on release `v2.10.1`.

## Expected behavior

Malformed shared-string indices should be rejected or treated as missing/invalid string references without panicking.

## Suggested remediation

Check both lower and upper bounds before indexing the shared string table. For example:

```go
if xlsxSI >= 0 && xlsxSI < len(d.SI) {
    return d.SI[xlsxSI].String(), nil
}
```

Add regression tests for `GetCellValue()` and `GetRows()` on `t="s"` cells whose `<v>` value is negative.

## References
- https://github.com/qax-os/excelize/security/advisories/GHSA-fx5j-qcqg-grpf
- https://nvd.nist.gov/vuln/detail/CVE-2026-59162
- https://github.com/qax-os/excelize/pull/2331
- https://github.com/qax-os/excelize/commit/93f0b3caed37f21ef5079e3259c6c21dcfe68453
- https://github.com/qax-os/excelize
- https://github.com/qax-os/excelize/releases/tag/v2.11.0
